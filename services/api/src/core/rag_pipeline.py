import logging
from typing import Generator, List, Optional

import elasticsearch
from core.component_factory import ModelProvider, PipelineComponentFactory
from core.document_manager import DocumentStoreManager
from core.model_manager import OllamaModelManager
from core.pipeline_config import QueryPipelineConfig
from haystack import Pipeline


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

    def __init__(self, config: QueryPipelineConfig, streaming_callback=None):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing RAGQueryPipeline")
        self.config = config
        self._streaming_callback = streaming_callback

        # Initialize document store manager
        self.doc_store_manager = DocumentStoreManager(config.es_url, config.es_index)
        self.document_store = self.doc_store_manager.initialize_store()

        # Only initialize Ollama model manager if using Ollama provider
        self.model_manager = None
        if config.provider == ModelProvider.OLLAMA:
            self.model_manager = OllamaModelManager(
                config.ollama_url, config.allow_model_pull
            )

        self.component_factory = PipelineComponentFactory(
            config, self.document_store, streaming_callback
        )
        self.query_pipeline = None

    def initialize_and_check_models(self) -> Generator[dict, None, None]:
        try:
            # Only perform Ollama-specific model checks if using Ollama
            if self.config.provider == ModelProvider.OLLAMA:
                if not self.model_manager:
                    raise ValueError(
                        "Ollama model manager not initialized but provider is set to Ollama"
                    )
                self.model_manager.check_server_health()
                yield from self._check_required_models()
            else:
                # For HuggingFace, we just yield a success status
                yield {
                    "type": "model_status",
                    "status": "success",
                    "message": "Using HuggingFace provider",
                }
        except Exception as e:
            self.logger.error(f"Failed to initialize models: {str(e)}", exc_info=True)
            yield {"type": "model_status", "status": "error", "error": str(e)}
            raise

    def _check_required_models(self) -> Generator[dict, None, None]:
        if self.model_manager:
            for model_name in [self.config.model_name, self.config.embedding_model]:
                yield from self.model_manager.verify_and_pull_model(model_name)

    def create_query_pipeline(self, use_embeddings: bool = True) -> Pipeline:
        self.logger.info("\nInitializing Query Pipeline Components:")

        try:
            query_pipeline = Pipeline()
            self.logger.info("Created new Pipeline instance")

            prompt_builder = self.component_factory.create_prompt_builder(
                self.QUERY_TEMPLATE
            )
            query_pipeline.add_component("prompt_builder", prompt_builder)

            if use_embeddings:
                text_embedder = self.component_factory.create_text_embedder()
                query_pipeline.add_component("text_embedder", text_embedder)

                retriever = self.component_factory.create_retriever()
                query_pipeline.add_component("retriever", retriever)

                query_pipeline.connect(
                    "text_embedder.embedding", "retriever.query_embedding"
                )
                query_pipeline.connect(
                    "retriever.documents", "prompt_builder.documents"
                )

            llm_generator = self.component_factory.create_generator()
            query_pipeline.add_component("llm", llm_generator)

            query_pipeline.connect("prompt_builder.prompt", "llm.prompt")

            self.query_pipeline = query_pipeline
            self.logger.info(
                f"Query Pipeline creation completed successfully (embeddings {'enabled' if use_embeddings else 'disabled'})"
            )
            return query_pipeline

        except Exception as e:
            self.logger.error(
                f"Failed to create query pipeline: {str(e)}", exc_info=True
            )
            raise

    def run_query(
        self,
        query: str,
        conversation: List[dict] = None,
        print_response: bool = False,
        use_embeddings: bool = True,
    ) -> Optional[dict]:
        self.logger.info(f"\nProcessing Query: {query}")
        self.logger.info(f"Conversation history present: {bool(conversation)}")

        if not self.query_pipeline:
            self.logger.info("Query pipeline not initialized. Creating new pipeline...")
            self.create_query_pipeline(use_embeddings=use_embeddings)

        try:
            self.logger.info("Executing query pipeline...")

            pipeline_inputs = {
                "prompt_builder": {
                    "query": query,
                    "system_prompt": self.config.system_prompt,
                    "conversation": conversation or [],
                },
            }

            if use_embeddings:
                pipeline_inputs["text_embedder"] = {"text": query}

            response = self.query_pipeline.run(pipeline_inputs)
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
