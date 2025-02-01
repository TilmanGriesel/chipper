from api.config import (
    BYPASS_OLLAMA_RAG,
    ENABLE_OLLAMA_PROXY,
    PROVIDER_IS_OLLAMA,
    logger,
)
from api.ollama_routes import setup_ollama_proxy_routes
from api.routes import register_health_routes, register_rag_chat_route
from flask import Flask


def setup_all_routes(app: Flask):
    try:
        if PROVIDER_IS_OLLAMA and ENABLE_OLLAMA_PROXY:
            # Setup Ollama proxy routes
            setup_ollama_proxy_routes(app)
            logger.info("Ollama proxy routes registered successfully")

        # Setup internal RAG pipeline routes
        if not BYPASS_OLLAMA_RAG or not PROVIDER_IS_OLLAMA:
            register_rag_chat_route(app)
            logger.info(
                "Chat routes registered successfully: RAG and embedding enabled."
            )
        else:
            logger.warning(
                "Chat routes bypassed! RAG is disabled, and embeddings will not be used."
            )

        # Setup health check routes
        register_health_routes(app)
        logger.info("Health check routes registered successfully")

    except Exception as e:
        logger.error(f"Error setting up routes: {e}", exc_info=True)
        raise
