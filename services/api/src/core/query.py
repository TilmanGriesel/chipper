import json
import logging
from dataclasses import dataclass
from typing import Generator, List, Optional

import elasticsearch
import requests
from haystack import Pipeline
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


class RAGQueryPipeline:
    QUERY_TEMPLATE = """
        {% if conversation %}
        Previous conversation:
        {% for message in conversation %}
        {{ message.role }}: {{ message.content }}
        {% endfor %}
        {% endif %}

        {{ system_prompt }}

        Context:
        {% for document in documents %}
            {{ document.content }}
            Source: {{ document.meta.file_path }}
        {% endfor %}

        Question: {{ query }}?
    """

    def __init__(
        self,
        config: QueryPipelineConfig,
        streaming_callback=None,
    ):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing RAGQueryPipeline")
        self.config = config
        self._streaming_callback = streaming_callback
        self._log_configuration()
        self.document_store = self._initialize_document_store()
        self.query_pipeline = None
        self.logger.info("RAGQueryPipeline initialization completed")

    def initialize_and_check_models(self) -> Generator[dict, None, None]:
        try:
            self._check_server_health()
            yield from self.check_and_pull_models()
        except Exception as e:
            self.logger.error(f"Failed to initialize models: {str(e)}", exc_info=True)
            yield {"type": "model_status", "status": "error", "error": str(e)}
            raise

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
                self.logger.info("Successfully connected to the Ollama server")
            else:
                self.logger.error(
                    f"Ollama server returned status code: {health_response.status_code}"
                )
                raise Exception("Ollama server connectivity check failed.")

        except requests.ConnectionError as e:
            self.logger.error(
                f"Connection error while checking Ollama server: {str(e)}",
                exc_info=True,
            )
            raise
        except Exception as e:
            self.logger.error(
                f"Error during Ollama server connectivity check: {str(e)}",
                exc_info=True,
            )
            raise

    def check_and_pull_models(self) -> Generator[dict, None, None]:
        for model_name in [self.config.model_name, self.config.embedding_model]:
            try:
                self.logger.info(f"Checking availability of model: {model_name}")
                yield {
                    "type": "model_status",
                    "status": "checking",
                    "model": model_name,
                }

                show_response = requests.post(
                    f"{self.config.ollama_url}/api/show",
                    json={"model": model_name},
                )

                if show_response.status_code != 200:
                    self.logger.info(
                        f"Model '{model_name}' not found locally, initiating pull..."
                    )
                    yield {
                        "type": "model_status",
                        "status": "pulling",
                        "model": model_name,
                    }

                    last_percentage = -1
                    pull_successful = False
                    with requests.post(
                        f"{self.config.ollama_url}/api/pull",
                        json={"model": model_name},
                        stream=True,
                    ) as response:
                        if response.status_code == 200:
                            for line in response.iter_lines():
                                if line:
                                    progress = json.loads(line)
                                    if "total" in progress and "completed" in progress:
                                        current_percentage = int(
                                            (progress["completed"] / progress["total"])
                                            * 100
                                        )
                                        if current_percentage > last_percentage:
                                            yield {
                                                "type": "model_status",
                                                "status": "progress",
                                                "model": model_name,
                                                "percentage": current_percentage,
                                            }
                                            last_percentage = current_percentage
                                            if current_percentage == 100:
                                                pull_successful = True

                            verify_response = requests.post(
                                f"{self.config.ollama_url}/api/show",
                                json={"model": model_name},
                            )

                            if verify_response.status_code == 200 and pull_successful:
                                yield {
                                    "type": "model_status",
                                    "status": "complete",
                                    "model": model_name,
                                }
                                self.logger.info(
                                    f"Model '{model_name}' pulled successfully"
                                )
                            else:
                                error_msg = (
                                    f"Model '{model_name}' not found after pull attempt"
                                )
                                self.logger.error(error_msg)
                                yield {
                                    "type": "model_status",
                                    "status": "error",
                                    "model": model_name,
                                    "error": error_msg,
                                }
                                raise Exception(error_msg)
                        else:
                            error_msg = f"Model pull failed: {response.text}"
                            self.logger.error(error_msg)
                            yield {
                                "type": "model_status",
                                "status": "error",
                                "model": model_name,
                                "error": error_msg,
                            }
                            raise Exception(error_msg)
                else:
                    yield {
                        "type": "model_status",
                        "status": "available",
                        "model": model_name,
                    }
                    self.logger.info(
                        f"Model '{model_name}' is already available locally"
                    )

            except Exception as e:
                error_msg = f"Failed to verify or pull model {model_name}: {str(e)}"
                self.logger.error(error_msg, exc_info=True)
                yield {
                    "type": "model_status",
                    "status": "error",
                    "model": model_name,
                    "error": error_msg,
                }
                raise

    def _initialize_models(self):
        try:
            self._check_server_health()
            for status in self.check_and_pull_models():
                self.logger.info(f"Model status update: {status}")
        except Exception as e:
            self.logger.error(f"Failed to initialize models: {str(e)}", exc_info=True)
            raise

    def _initialize_document_store(self) -> ElasticsearchDocumentStore:
        try:
            self.logger.info(
                f"Initializing Elasticsearch document store at {self.config.es_url}"
            )
            document_store = ElasticsearchDocumentStore(
                hosts=self.config.es_url,
                index=self.config.es_index,
            )
            doc_count = document_store.count_documents()
            self.logger.info(
                f"Document store initialized successfully. Index '{self.config.es_index}' contains {doc_count} documents"
            )
            return document_store

        except elasticsearch.ConnectionError as e:
            self.logger.error(
                f"Failed to connect to Elasticsearch at {self.config.es_url}: {str(e)}",
                exc_info=True,
            )
            raise
        except Exception as e:
            self.logger.error(
                f"Failed to initialize document store: {str(e)}", exc_info=True
            )
            raise

    def create_query_pipeline(self) -> Pipeline:
        self.logger.info("\nInitializing Query Pipeline Components:")

        try:
            query_pipeline = Pipeline()
            self.logger.info("Created new Pipeline instance")

            text_embedder = self._create_text_embedder()
            query_pipeline.add_component("text_embedder", text_embedder)
            self.logger.info("Text embedder component added to pipeline")

            retriever = self._create_retriever()
            query_pipeline.add_component("retriever", retriever)
            self.logger.info("Retriever component added to pipeline")

            prompt_builder = PromptBuilder(template=self.QUERY_TEMPLATE)
            query_pipeline.add_component("prompt_builder", prompt_builder)
            self.logger.info("Prompt builder component added to pipeline")

            ollama_generator = self._create_ollama_generator()
            query_pipeline.add_component("llm", ollama_generator)
            self.logger.info("Ollama generator component added to pipeline")

            self._connect_pipeline_components(query_pipeline)
            self.logger.info("Pipeline components successfully connected")

            self.query_pipeline = query_pipeline
            self.logger.info("Query Pipeline creation completed successfully")

            return query_pipeline

        except Exception as e:
            self.logger.error(
                f"Failed to create query pipeline: {str(e)}", exc_info=True
            )
            raise

    def _create_text_embedder(self) -> OllamaTextEmbedder:
        self.logger.info(
            f"Initializing Text Embedder with model: {self.config.embedding_model}"
        )
        embedder = OllamaTextEmbedder(
            model=self.config.embedding_model, url=self.config.ollama_url
        )
        self.logger.info("Text Embedder initialized successfully")
        return embedder

    def _create_retriever(self) -> ElasticsearchEmbeddingRetriever:
        self.logger.info(
            f"Initializing Elasticsearch Retriever with top_k={self.config.top_k}"
        )
        retriever = ElasticsearchEmbeddingRetriever(
            document_store=self.document_store,
            top_k=self.config.top_k,
        )
        self.logger.info("Elasticsearch Retriever initialized successfully")
        return retriever

    def _create_ollama_generator(self) -> OllamaGenerator:
        self.logger.info(
            f"Initializing Ollama Generator with model: {self.config.model_name}"
        )
        generation_kwargs = {
            "temperature": self.config.temperature,
            "context_length": self.config.context_window,
        }

        if self.config.seed != 0:
            generation_kwargs["seed"] = self.config.seed
            self.logger.info(f"Using seed value: {self.config.seed}")

        generator = OllamaGenerator(
            model=self.config.model_name,
            url=self.config.ollama_url,
            generation_kwargs=generation_kwargs,
            streaming_callback=self._streaming_callback,
            timeout=240,
        )
        self.logger.info("Ollama Generator initialized successfully")
        return generator

    def _connect_pipeline_components(self, pipeline: Pipeline):
        self.logger.info("Connecting pipeline components...")
        pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
        pipeline.connect("retriever.documents", "prompt_builder.documents")
        pipeline.connect("prompt_builder.prompt", "llm.prompt")
        self.logger.info("Pipeline components connected successfully")

    def run_query(
        self, query: str, conversation: List[dict] = None, print_response: bool = False
    ) -> Optional[dict]:
        self.logger.info(f"\nProcessing Query: {query}")
        self.logger.info(f"Conversation history present: {bool(conversation)}")

        if not self.query_pipeline:
            self.logger.info("Query pipeline not initialized. Creating new pipeline...")
            self.create_query_pipeline()

        try:
            self.logger.info("Executing query pipeline...")
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
            self.logger.info("Query pipeline execution completed successfully")

            if print_response and response["llm"]["replies"]:
                print(response["llm"]["replies"][0])
                print("\n")

            return response

        except elasticsearch.BadRequestError as e:
            self.logger.error(f"Elasticsearch bad request error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in query pipeline: {e}")
            raise
