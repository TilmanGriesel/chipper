import hashlib
import logging
import os
from typing import List, Optional, Dict, Any

from haystack import Document, Pipeline
from haystack.components.writers import DocumentWriter
from haystack.document_stores.types import DuplicatePolicy
from haystack_integrations.components.embedders.ollama import OllamaDocumentEmbedder, OllamaTextEmbedder
from haystack_integrations.document_stores.elasticsearch import ElasticsearchDocumentStore


def generate_document_id(file_path: str, content: str) -> str:
    unique_str = f"{file_path}:{content}"
    return hashlib.md5(unique_str.encode("utf-8")).hexdigest()


class DocumentEmbedder:
    def __init__(self, document_store: ElasticsearchDocumentStore, ollama_url: str, embedding_model: str):
        self.logger = logging.getLogger(__name__)
        self.document_store = document_store
        self.ollama_url = ollama_url
        self.embedding_model = embedding_model
        self.embedding_pipeline = None
        self.embedding_dimension = None
        try:
            self._validate_or_set_embedding_dimension()
        except Exception as e:
            self.logger.debug(str(e))

    def create_embedding_pipeline(self) -> Optional[Pipeline]:
        try:
            self.logger.debug("Setting up embedding pipeline")
            embedding_pipeline = Pipeline()
            document_embedder = OllamaDocumentEmbedder(model=self.embedding_model, url=self.ollama_url)
            embedding_pipeline.add_component("embedder", document_embedder)
            writer = DocumentWriter(document_store=self.document_store, policy=DuplicatePolicy.OVERWRITE)
            embedding_pipeline.add_component("writer", writer)
            embedding_pipeline.connect("embedder", "writer")
            self.embedding_pipeline = embedding_pipeline
            return embedding_pipeline
        except Exception as e:
            self.logger.debug(str(e))
            return None

    def _validate_or_set_embedding_dimension(self) -> None:
        try:
            docs = self.document_store._search_documents(size=1)
            if docs and len(docs) > 0 and hasattr(docs[0], "embedding") and docs[0].embedding is not None:
                self.embedding_dimension = len(docs[0].embedding)
                self.logger.debug(str(self.embedding_dimension))
        except Exception as e:
            self.logger.debug(str(e))

    def get_embedding_dimension(self, text: str = "test query") -> Optional[int]:
        if self.embedding_dimension is not None:
            return self.embedding_dimension
        try:
            text_embedder = OllamaTextEmbedder(model=self.embedding_model, url=self.ollama_url)
            embedding = text_embedder.run(text=text)["embedding"]
            self.embedding_dimension = len(embedding)
            self.logger.debug(str(self.embedding_dimension))
            return self.embedding_dimension
        except Exception as e:
            self.logger.debug(str(e))
            return None

    def _validate_documents(self, documents: List[Document]) -> List[Document]:
        valid_documents = []
        for doc in documents:
            try:
                if isinstance(doc, Document) and hasattr(doc, "content") and doc.content is not None:
                    valid_documents.append(doc)
                else:
                    self.logger.debug(str(doc))
            except Exception as e:
                self.logger.debug(str(e))
        return valid_documents

    def embed_documents(self, documents: List[Document], clear_index: bool = False) -> Dict[str, Any]:
        if clear_index:
            self.logger.warning("Clearing all documents from the Elasticsearch index is not implemented yet.")

        embedding_result = {
            "success": False,
            "documents_processed": 0,
            "documents_failed": 0,
            "error": None
        }

        if not documents:
            self.logger.debug("No documents provided for embedding")
            embedding_result["error"] = "No documents provided"
            return embedding_result

        valid_documents = self._validate_documents(documents)
        if not valid_documents:
            self.logger.debug("No valid documents found after validation")
            embedding_result["error"] = "No valid documents"
            embedding_result["documents_failed"] = len(documents)
            return embedding_result

        if not self.embedding_pipeline:
            self.embedding_pipeline = self.create_embedding_pipeline()
            if not self.embedding_pipeline:
                embedding_result["error"] = "Failed to create embedding pipeline"
                embedding_result["documents_failed"] = len(valid_documents)
                return embedding_result

        try:
            self.logger.debug(f"Attempting to embed {len(valid_documents)} documents")
            self.embedding_pipeline.run({"embedder": {"documents": valid_documents}})
            embedding_result["success"] = True
            embedding_result["documents_processed"] = len(valid_documents)
            embedding_result["documents_failed"] = len(documents) - len(valid_documents)
        except Exception as e:
            self.logger.debug(str(e))
            embedding_result["error"] = str(e)
            embedding_result["documents_failed"] = len(valid_documents)

        return embedding_result

    def embed_files(self, file_paths: List[str], clear_index: bool = False) -> Dict[str, Any]:
        documents = []
        for file_path in file_paths:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                doc_id = generate_document_id(file_path, content)
                doc = Document(id=doc_id, content=content, meta={"filename": os.path.basename(file_path)})
                documents.append(doc)
            except Exception as e:
                self.logger.debug(str(e))
        return self.embed_documents(documents, clear_index=clear_index)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    document_store = ElasticsearchDocumentStore(
        host="localhost",
        port=9200,
        username="",
        password="",
        index="my-haystack-index",
        embedding_field="embedding"
    )
    embedder = DocumentEmbedder(document_store, "http://localhost:11434", "nomic-embed-text")
    files_to_embed = [
        "/path/to/first_file.txt",
        "/path/to/some_other_file.txt"
    ]
    result = embedder.embed_files(files_to_embed, clear_index=True)
    print(result)
