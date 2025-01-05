import logging

from haystack.components.builders.prompt_builder import PromptBuilder
from haystack_integrations.components.embedders.ollama import OllamaTextEmbedder
from haystack_integrations.components.generators.ollama import OllamaGenerator
from haystack_integrations.components.retrievers.elasticsearch import ElasticsearchEmbeddingRetriever
from haystack_integrations.document_stores.elasticsearch import ElasticsearchDocumentStore

from core.pipeline_config import QueryPipelineConfig


class PipelineComponentFactory:
    def __init__(self, config: QueryPipelineConfig, document_store: ElasticsearchDocumentStore,
                 streaming_callback=None):
        self.config = config
        self.document_store = document_store
        self.streaming_callback = streaming_callback
        self.logger = logging.getLogger(__name__)

    def create_text_embedder(self) -> OllamaTextEmbedder:
        self.logger.info(f"Initializing Text Embedder with model: {self.config.embedding_model}")
        embedder = OllamaTextEmbedder(
            model=self.config.embedding_model,
            url=self.config.ollama_url
        )
        self.logger.info("Text Embedder initialized successfully")
        return embedder

    def create_retriever(self) -> ElasticsearchEmbeddingRetriever:
        self.logger.info(f"Initializing Elasticsearch Retriever with top_k={self.config.top_k}")
        retriever = ElasticsearchEmbeddingRetriever(
            document_store=self.document_store,
            top_k=self.config.top_k,
        )
        self.logger.info("Elasticsearch Retriever initialized successfully")
        return retriever

    def create_prompt_builder(self, template: str) -> PromptBuilder:
        self.logger.info("Initializing Prompt Builder")
        return PromptBuilder(template=template)

    def create_ollama_generator(self) -> OllamaGenerator:
        self.logger.info(f"Initializing Ollama Generator with model: {self.config.model_name}")
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
            streaming_callback=self.streaming_callback,
            timeout=240,
        )
        self.logger.info("Ollama Generator initialized successfully")
        return generator
