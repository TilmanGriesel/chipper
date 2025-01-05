import logging

import elasticsearch
from haystack_integrations.document_stores.elasticsearch import (
    ElasticsearchDocumentStore,
)


class DocumentStoreManager:
    def __init__(self, es_url: str, es_index: str):
        self.logger = logging.getLogger(__name__)
        self.es_url = es_url
        self.es_index = es_index
        self.document_store = None

    def initialize_store(self) -> ElasticsearchDocumentStore:
        try:
            self.logger.info(
                f"Initializing Elasticsearch document store at {self.es_url}"
            )
            self.document_store = ElasticsearchDocumentStore(
                hosts=self.es_url,
                index=self.es_index,
            )
            doc_count = self.document_store.count_documents()
            self.logger.info(
                f"Document store initialized successfully. Index '{self.es_index}' contains {doc_count} documents"
            )
            return self.document_store

        except elasticsearch.ConnectionError as e:
            self.logger.error(
                f"Failed to connect to Elasticsearch at {self.es_url}: {str(e)}",
                exc_info=True,
            )
            raise
        except Exception as e:
            self.logger.error(
                f"Failed to initialize document store: {str(e)}", exc_info=True
            )
            raise
