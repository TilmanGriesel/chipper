import logging
import os
import requests
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict

import elasticsearch
from haystack import Pipeline, Document
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack_integrations.components.embedders.ollama import OllamaTextEmbedder
from haystack_integrations.components.generators.ollama import OllamaGenerator
from haystack_integrations.components.retrievers.elasticsearch import (
    ElasticsearchEmbeddingRetriever,
)
from haystack_integrations.document_stores.elasticsearch import (
    ElasticsearchDocumentStore,
)


@dataclass
class PipelineConfig:
    es_url: str
    es_index: str
    ollama_url: str
    embedding_model: str


@dataclass
class QueryPipelineConfig(PipelineConfig):
    model_name: str
    system_prompt: str
    context_window: int
    temperature: float
    seed: int
    top_k: int


class MetricsTracker:
    def __init__(self):
        self.metrics = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "avg_response_time": 0,
            "total_tokens_used": 0,
            "retrieval_stats": {
                "total_documents_retrieved": 0,
                "avg_relevance_score": 0,
            },
        }

    def update_query_metrics(self, response: Dict, execution_time: float, logger):
        try:
            self.metrics["total_queries"] += 1
            self.metrics["successful_queries"] += 1

            n = self.metrics["successful_queries"]
            current_avg = self.metrics["avg_response_time"]
            self.metrics["avg_response_time"] = (
                current_avg * (n - 1) + execution_time
            ) / n

            retrieved_docs = response.get("retriever", {}).get("documents", [])
            num_docs = len(retrieved_docs)
            self.metrics["retrieval_stats"]["total_documents_retrieved"] += num_docs

            avg_score = 0.0
            if num_docs > 0:
                scores = [doc.score for doc in retrieved_docs if hasattr(doc, "score")]
                if scores:
                    avg_score = sum(scores) / len(scores)
                    self.metrics["retrieval_stats"]["avg_relevance_score"] = (
                        self.metrics["retrieval_stats"]["avg_relevance_score"] * (n - 1)
                        + avg_score
                    ) / n

            self._log_execution_metrics(
                execution_time, num_docs, avg_score, response, logger
            )

        except Exception as e:
            logger.error(f"Error logging metrics: {str(e)}", exc_info=True)

    @staticmethod
    def _log_execution_metrics(
        execution_time: float, num_docs: int, avg_score: float, response: Dict, logger
    ):
        logger.info("\nQuery Execution Metrics:")
        logger.info(f"- Execution time: {execution_time:.2f} seconds")
        logger.info(f"- Retrieved documents: {num_docs}")
        if avg_score > 0:
            logger.info(f"- Average relevance score: {avg_score:.4f}")

        if "llm" in response and response["llm"].get("replies"):
            response_length = len(response["llm"]["replies"][0])
            logger.info(f"- Response length: {response_length} characters")


class RAGQueryPipeline:
    QUERY_TEMPLATE = """
        {{ system_prompt }}

        {% if conversation %}
        Previous conversation:
        {% for message in conversation %}
        {{ message.role }}: {{ message.content }}
        {% endfor %}
        {% endif %}

        Given the above conversation and the following information, answer the question.
        Ignore your own knowledge.

        Context:
        {% for document in documents %}
            {{ document.content }}
            Source: {{ document.meta.file_path }}
        {% endfor %}

        Question: {{ query }}?
    """

    def __init__(
        self,
        es_url: str = None,
        es_index: str = None,
        ollama_url: str = None,
        model_name: str = None,
        embedding_model: str = None,
        system_prompt: str = None,
        context_window: int = 4096,
        temperature: float = 0.7,
        seed: int = 0,
        top_k: int = 5,
    ):
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=logging.INFO,
        )
        self.logger = logging.getLogger(__name__)

        self.config = QueryPipelineConfig(
            es_url=es_url or os.getenv("ES_URL"),
            es_index=es_index or os.getenv("ES_INDEX"),
            ollama_url=ollama_url or os.getenv("OLLAMA_URL"),
            embedding_model=embedding_model or os.getenv("EMBEDDING_MODEL"),
            model_name=model_name or os.getenv("MODEL_NAME"),
            system_prompt=system_prompt
            or os.getenv("SYSTEM_PROMPT", "You are a helpful assistant."),
            context_window=int(os.getenv("CONTEXT_WINDOW", "4096")),
            temperature=float(os.getenv("TEMPERATURE", "0.8")),
            seed=int(os.getenv("SEED", "0")),
            top_k=int(os.getenv("TOP_K", "5")),
        )

        self._log_configuration()
        self.document_store = self._initialize_document_store()
        self._initialize_query()
        self.query_pipeline = None
        self.metrics_tracker = MetricsTracker()

    def _log_configuration(self):
        self.logger.info("\nQuery Pipeline Configuration:")
        for field_name, field_value in self.config.__dict__.items():
            self.logger.info(f"- {field_name}: {field_value}")

    def _check_server_health(self):
        try:
            self.logger.info(
                f"Checking connectivity to Ollama server at {self.config.ollama_url}"
            )
            health_response = requests.get(self.config.ollama_url)

            if health_response.status_code == 200:
                self.logger.info(
                    f"Successfully connected to the Ollama server, Response: {health_response.text}"
                )
            else:
                self.logger.error(
                    f"Failed to connect to the Ollama server. "
                    f"Status code: {health_response.status_code}, Response: {health_response.text}"
                )
                raise Exception("Ollama server connectivity check failed.")

        except Exception as e:
            self.logger.error(
                f"Error during Ollama server connectivity check: {str(e)}",
                exc_info=True,
            )
            raise

    def _initialize_query(self):
        try:
            self._check_server_health()

            self.logger.info(f"Checking model: {self.config.model_name}")
            show_response = requests.post(
                f"{self.config.ollama_url}/api/show",
                json={"model": self.config.model_name},
            )

            if show_response.status_code != 200:
                self.logger.info(f"Pulling model '{self.config.model_name}'...")
                pull_response = requests.post(
                    f"{self.config.ollama_url}/api/pull",
                    json={"model": self.config.model_name},
                )

                if pull_response.status_code == 200:
                    self.logger.info(
                        f"Embedding model '{self.config.model_name}' pulled successfully."
                    )
                else:
                    self.logger.error(f"Failed to pull model: {pull_response.text}")
                    raise Exception(f"Model pull failed: {pull_response.text}")
            else:
                self.logger.info(
                    f"Model '{self.config.model_name}' is already available."
                )

        except Exception as e:
            self.logger.error(
                f"Failed to verify or pull model: {str(e)}", exc_info=True
            )
            raise

    def _initialize_document_store(self) -> ElasticsearchDocumentStore:
        try:
            document_store = ElasticsearchDocumentStore(
                hosts=self.config.es_url,
                index=self.config.es_index,
            )
            doc_count = document_store.count_documents()
            self.logger.info(
                f"Document store initialized successfully with {doc_count} documents"
            )

            index_stats = document_store.client.indices.stats()
            self.logger.info("Index Statistics:")
            self.logger.info(
                f"- Total size: {index_stats['_all']['total']['store']['size_in_bytes'] / 1024 / 1024:.2f} MB"
            )
            self.logger.info(
                f"- Document count: {index_stats['_all']['total']['docs']['count']}"
            )
            return document_store

        except Exception as e:
            self.logger.error(
                f"Failed to initialize document store: {str(e)}", exc_info=True
            )
            raise

    def create_query_pipeline(self) -> Pipeline:
        self.logger.info("\nInitializing Query Pipeline Components:")

        try:
            query_pipeline = Pipeline()

            text_embedder = self._create_text_embedder()
            query_pipeline.add_component("text_embedder", text_embedder)

            retriever = self._create_retriever()
            query_pipeline.add_component("retriever", retriever)

            prompt_builder = PromptBuilder(template=self.QUERY_TEMPLATE)
            query_pipeline.add_component("prompt_builder", prompt_builder)

            ollama_generator = self._create_ollama_generator()
            query_pipeline.add_component("llm", ollama_generator)

            self._connect_pipeline_components(query_pipeline)
            self.query_pipeline = query_pipeline
            self.logger.info("Query Pipeline successfully created")

            return query_pipeline

        except Exception as e:
            self.logger.error(
                f"Failed to create query pipeline: {str(e)}", exc_info=True
            )
            raise

    def _create_text_embedder(self) -> OllamaTextEmbedder:
        self.logger.info(
            f"- Initializing Text Embedder with model: {self.config.embedding_model}"
        )
        embedder = OllamaTextEmbedder(
            model=self.config.embedding_model, url=self.config.ollama_url
        )
        self.logger.info(f"- Ollama Text Embedder Configuration:")
        self.logger.info(f"  - Model: {self.config.embedding_model}")
        self.logger.info(f"  - URL: {self.config.ollama_url}")
        return embedder

    def _create_retriever(self) -> ElasticsearchEmbeddingRetriever:
        self.logger.info("- Initializing Elasticsearch Retriever")
        retriever = ElasticsearchEmbeddingRetriever(
            document_store=self.document_store,
            top_k=self.config.top_k,
        )
        self.logger.info(f"Retriever configuration:")
        self.logger.info(f"- Document store URL: {self.config.es_url}")
        self.logger.info(
            f"- Number of documents in store: {self.document_store.count_documents()}"
        )
        return retriever

    def _create_ollama_generator(self) -> OllamaGenerator:
        self.logger.info(f"- Initializing Ollama Generator")
        generation_kwargs = {
            "temperature": self.config.temperature,
            "context_length": self.config.context_window,
        }

        if self.config.seed != 0:
            generation_kwargs["seed"] = self.config.seed

        generator = OllamaGenerator(
            model=self.config.model_name,
            url=self.config.ollama_url,
            generation_kwargs=generation_kwargs,
        )
        self._log_generator_config()
        return generator

    def _log_generator_config(self):
        self.logger.info(f"- Ollama Generator Configuration:")
        self.logger.info(f"  - Model: {self.config.model_name}")
        self.logger.info(f"  - URL: {self.config.ollama_url}")
        self.logger.info(f"  - Temperature: {self.config.temperature}")
        self.logger.info(f"  - Context Length: {self.config.context_window}")
        if self.config.seed != 0:
            self.logger.info(f"  - Seed: {self.config.seed}")
        else:
            self.logger.info("  - Seed: Not applied")

    def _connect_pipeline_components(self, pipeline: Pipeline):
        pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
        pipeline.connect("retriever.documents", "prompt_builder.documents")
        pipeline.connect("prompt_builder.prompt", "llm.prompt")

    def run_query(
        self, query: str, conversation: List[dict] = None, print_response: bool = True
    ) -> Optional[dict]:
        self.logger.info(f"\nProcessing Query:")
        self.logger.info(f"- Query text: {query}")
        self.logger.info(
            f"- Conversation history length: {len(conversation) if conversation else 0}"
        )

        if not self.query_pipeline:
            self.create_query_pipeline()

        try:
            start_time = datetime.now()
            self.logger.info("Running pipeline steps...")

            try:
                response = self.query_pipeline.run(
                    {
                        "text_embedder": {"text": query},
                        "prompt_builder": {
                            "query": query,
                            "system_prompt": self.config.system_prompt,
                            "conversation": conversation or [],
                        },
                    }
                )
            except elasticsearch.BadRequestError as e:
                self.logger.error(f"Elasticsearch bad request error: {e}")
                raise
            except Exception as e:
                self.logger.error(f"Unexpected error in query pipeline: {e}")
                raise

            execution_time = (datetime.now() - start_time).total_seconds()
            self.metrics_tracker.update_query_metrics(
                response, execution_time, self.logger
            )

            if print_response:
                reply = (
                    response["llm"]["replies"][0]
                    if response["llm"]["replies"]
                    else "No response"
                )
                self.logger.info("\nGenerated Response:")
                print(reply)
                print("\n")

            return response

        except Exception as e:
            self.metrics_tracker.metrics["failed_queries"] += 1
            self.logger.error(f"Query execution failed: {str(e)}", exc_info=True)
            raise

    def get_pipeline_stats(self) -> Dict:
        return {
            "pipeline_metrics": self.metrics_tracker.metrics,
            "document_store": {
                "total_documents": self.document_store.count_documents(),
                "index_stats": self.document_store.client.indices.stats(),
            },
        }
