import logging
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

import elasticsearch
import requests
from haystack import Pipeline
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.dataclasses import StreamingChunk
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
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=logging.INFO,
        )
        self.logger = logging.getLogger(__name__)

        self.config = config
        self._streaming_callback = streaming_callback
        self._log_configuration()
        self.document_store = self._initialize_document_store()
        self._initialize_query()
        self.query_pipeline = None

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
        return OllamaTextEmbedder(
            model=self.config.embedding_model, url=self.config.ollama_url
        )

    def _create_retriever(self) -> ElasticsearchEmbeddingRetriever:
        self.logger.info("- Initializing Elasticsearch Retriever")
        return ElasticsearchEmbeddingRetriever(
            document_store=self.document_store,
            top_k=self.config.top_k,
        )

    def _create_ollama_generator(self) -> OllamaGenerator:
        self.logger.info(f"- Initializing Ollama Generator")
        generation_kwargs = {
            "temperature": self.config.temperature,
            "context_length": self.config.context_window,
        }

        if self.config.seed != 0:
            generation_kwargs["seed"] = self.config.seed

        return OllamaGenerator(
            model=self.config.model_name,
            url=self.config.ollama_url,
            generation_kwargs=generation_kwargs,
            streaming_callback=self._streaming_callback,
        )

    def _connect_pipeline_components(self, pipeline: Pipeline):
        pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
        pipeline.connect("retriever.documents", "prompt_builder.documents")
        pipeline.connect("prompt_builder.prompt", "llm.prompt")

    def run_query(
        self, query: str, conversation: List[dict] = None, print_response: bool = False
    ) -> Optional[dict]:
        self.logger.info(f"\nProcessing Query: {query}")

        if not self.query_pipeline:
            self.create_query_pipeline()

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
