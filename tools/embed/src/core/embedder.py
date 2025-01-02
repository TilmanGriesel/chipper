import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import List

import requests
from core.document_embedder import DocumentEmbedder
from haystack import Document
from haystack_integrations.document_stores.elasticsearch import (
    ElasticsearchDocumentStore,
)


@dataclass
class PipelineConfig:
    es_url: str
    es_index: str
    ollama_url: str
    embedding_model: str


class MetricsTracker:
    def __init__(self):
        self.metrics = {
            "total_documents": 0,
            "successful_embeddings": 0,
            "failed_embeddings": 0,
            "avg_embedding_time": 0,
            "total_tokens_used": 0,
        }

    def update_embedding_metrics(self, execution_time: float):
        self.metrics["total_documents"] += 1
        self.metrics["successful_embeddings"] += 1

        n = self.metrics["successful_embeddings"]
        current_avg = self.metrics["avg_embedding_time"]
        self.metrics["avg_embedding_time"] = (
            current_avg * (n - 1) + execution_time
        ) / n

    def log_metrics(self, logger):
        logger.info("\nEmbedding Metrics:")
        logger.info(f"- Total documents processed: {self.metrics['total_documents']}")
        logger.info(f"- Successful embeddings: {self.metrics['successful_embeddings']}")
        logger.info(f"- Failed embeddings: {self.metrics['failed_embeddings']}")
        logger.info(
            f"- Average embedding time per document: {self.metrics['avg_embedding_time']:.2f} seconds"
        )


class RAGEmbedder:
    def __init__(
        self,
        es_url: str = None,
        es_index: str = None,
        ollama_url: str = None,
        embedding_model: str = None,
    ):
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=logging.INFO,
        )
        self.logger = logging.getLogger(__name__)

        self.config = PipelineConfig(
            es_url=es_url or os.getenv("ES_URL"),
            es_index=es_index or os.getenv("ES_INDEX"),
            ollama_url=ollama_url or os.getenv("OLLAMA_URL"),
            embedding_model=embedding_model or os.getenv("EMBEDDING_MODEL"),
        )

        self._log_configuration()
        self.document_store = self._initialize_document_store()
        self._initialize_embedder()
        self.metrics_tracker = MetricsTracker()

    def _log_configuration(self):
        self.logger.info("\nEmbedding Pipeline Configuration:")
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

    def _initialize_embedder(self):
        try:
            self._check_server_health()

            self.logger.info(f"Checking embedding model: {self.config.embedding_model}")
            show_response = requests.post(
                f"{self.config.ollama_url}/api/show",
                json={"model": self.config.embedding_model},
            )

            if show_response.status_code != 200:
                self.logger.info(f"Pulling model '{self.config.embedding_model}'...")
                pull_response = requests.post(
                    f"{self.config.ollama_url}/api/pull",
                    json={"model": self.config.embedding_model},
                )

                if pull_response.status_code == 200:
                    self.logger.info(
                        f"Embedding model '{self.config.embedding_model}' pulled successfully."
                    )
                else:
                    self.logger.error(
                        f"Failed to pull embedding model: {pull_response.text}"
                    )
                    raise Exception(
                        f"Embedding model pull failed: {pull_response.text}"
                    )
            else:
                self.logger.info(
                    f"Embedding model '{self.config.embedding_model}' is already available."
                )

        except Exception as e:
            self.logger.error(
                f"Failed to verify or pull embedding model: {str(e)}", exc_info=True
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

    def embed_documents(self, documents: List[Document]) -> None:
        start_time = datetime.now()
        total_chars = sum(len(doc.content) for doc in documents)

        self.logger.info("Starting document embedding process:")
        self.logger.info(f"- Total documents: {len(documents)}")
        self.logger.info(f"- Total characters: {total_chars}")

        try:
            embedder = DocumentEmbedder(
                document_store=self.document_store,
                ollama_url=self.config.ollama_url,
                embedding_model=self.config.embedding_model,
            )
            embedder.embed_documents(documents)

            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.info("Document embedding completed:")
            self.logger.info(f"- Execution time: {execution_time:.2f} seconds")
            self.logger.info(
                f"- Average time per document: {execution_time / len(documents):.2f} seconds"
            )

            self.metrics_tracker.update_embedding_metrics(execution_time)

        except Exception as e:
            self.logger.error(f"Document embedding failed: {str(e)}", exc_info=True)
            self.metrics_tracker.metrics["failed_embeddings"] += 1
            raise

    def finalize(self):
        self.metrics_tracker.log_metrics(self.logger)
