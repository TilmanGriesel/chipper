import logging
from typing import Callable, Optional

from core.pipeline_config import ModelProvider, QueryPipelineConfig
from haystack.components.builders.prompt_builder import PromptBuilder
from haystack.components.embedders import HuggingFaceAPITextEmbedder
from haystack.components.generators import HuggingFaceAPIGenerator
from haystack.utils import Secret
from haystack_integrations.components.embedders.ollama import OllamaTextEmbedder
from haystack_integrations.components.generators.ollama import OllamaGenerator
from haystack_integrations.components.retrievers.elasticsearch import (
    ElasticsearchEmbeddingRetriever,
)
from haystack_integrations.document_stores.elasticsearch import (
    ElasticsearchDocumentStore,
)


class PipelineComponentFactory:
    def __init__(
        self,
        config: QueryPipelineConfig,
        document_store: ElasticsearchDocumentStore,
        streaming_callback: Optional[Callable] = None,
    ):
        self.config = config
        self.document_store = document_store
        self.streaming_callback = streaming_callback
        self.logger = logging.getLogger(__name__)

    def create_text_embedder(self):
        self.logger.info(
            f"Initializing Text Embedder with model: {self.config.embedding_model}"
        )

        if self.config.provider == ModelProvider.OLLAMA:
            embedder = OllamaTextEmbedder(
                model=self.config.embedding_model, url=self.config.ollama_url
            )
        elif self.config.provider == ModelProvider.HUGGINGFACE:
            if not self.config.hf_api_key:
                raise ValueError(
                    "HuggingFace API key is required for HuggingFace provider"
                )

            embedder = HuggingFaceAPITextEmbedder(
                api_type="serverless_inference_api",
                api_params={"model": self.config.embedding_model},
                token=Secret.from_token(self.config.hf_api_key),
            )
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")

        self.logger.info("Text Embedder initialized successfully")
        return embedder

    def create_retriever(self) -> ElasticsearchEmbeddingRetriever:
        """Create Elasticsearch retriever."""
        self.logger.info(
            f"Initializing Elasticsearch Retriever with top_k={self.config.es_top_k} and num_candidates={self.config.es_num_candidates}"
        )
        retriever = ElasticsearchEmbeddingRetriever(
            document_store=self.document_store,
            top_k=(
                self.config.es_top_k
                if self.config.es_top_k is not None and self.config.es_top_k > 0
                else None
            ),
            num_candidates=(
                self.config.es_num_candidates
                if self.config.es_num_candidates is not None
                and self.config.es_num_candidates > 0
                else None
            ),
        )
        self.logger.info("Elasticsearch Retriever initialized successfully")
        return retriever

    def create_prompt_builder(self, template: str) -> PromptBuilder:
        """Create prompt builder with specified template."""
        self.logger.info("Initializing Prompt Builder")
        return PromptBuilder(template=template)

    def create_generator(self):
        """Create text generator based on provider configuration."""
        self.logger.info(f"Initializing Generator with model: {self.config.model_name}")

        if self.config.provider == ModelProvider.OLLAMA:
            generation_kwargs = {}

            # Core generation parameters
            if self.config.temperature is not None:
                generation_kwargs["temperature"] = self.config.temperature
            if self.config.context_window is not None:
                generation_kwargs["context_length"] = self.config.context_window
            if self.config.seed is not None and self.config.seed > 0:
                generation_kwargs["seed"] = self.config.seed
            if self.config.top_k is not None:
                generation_kwargs["top_k"] = self.config.top_k

            # Advanced sampling parameters
            if self.config.top_p is not None:
                generation_kwargs["top_p"] = self.config.top_p
            if self.config.min_p is not None:
                generation_kwargs["min_p"] = self.config.min_p

            # Mirostat parameters
            if self.config.mirostat is not None:
                generation_kwargs["mirostat"] = self.config.mirostat
            if self.config.mirostat_eta is not None:
                generation_kwargs["mirostat_eta"] = self.config.mirostat_eta
            if self.config.mirostat_tau is not None:
                generation_kwargs["mirostat_tau"] = self.config.mirostat_tau

            # Repetition control
            if self.config.repeat_last_n is not None:
                generation_kwargs["repeat_last_n"] = self.config.repeat_last_n
            if self.config.repeat_penalty is not None:
                generation_kwargs["repeat_penalty"] = self.config.repeat_penalty

            # Generation control
            if self.config.num_predict is not None:
                generation_kwargs["num_predict"] = self.config.num_predict
            if self.config.tfs_z is not None:
                generation_kwargs["tfs_z"] = self.config.tfs_z

            # Optional stop sequence
            if self.config.stop_sequence:
                generation_kwargs["stop"] = self.config.stop_sequence

            logging.info(f"Generation kwargs: {generation_kwargs}")

            # Instantiate generator
            generator = OllamaGenerator(
                model=self.config.model_name,
                url=self.config.ollama_url,
                generation_kwargs=generation_kwargs,
                streaming_callback=self.streaming_callback,
                timeout=240,
            )
        elif self.config.provider == ModelProvider.HUGGINGFACE:
            if not self.config.hf_api_key:
                raise ValueError(
                    "HuggingFace API key is required for HuggingFace provider"
                )

            generator = HuggingFaceAPIGenerator(
                api_type="serverless_inference_api",
                api_params={
                    "model": self.config.model_name,
                    "temperature": self.config.temperature,
                    "max_length": self.config.context_window,
                    "system_prompt": self.config.system_prompt,
                },
                token=Secret.from_token(self.config.hf_api_key),
                streaming_callback=self.streaming_callback,
            )
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")

        self.logger.info("Generator initialized successfully")
        return generator
