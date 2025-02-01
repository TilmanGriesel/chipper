from api.config import PROVIDER_IS_OLLAMA, logger
from api.ollama_routes import setup_ollama_routes
from api.routes import register_chat_routes, register_health_routes
from flask import Flask


def setup_all_routes(app: Flask):
    try:
        if PROVIDER_IS_OLLAMA:
            # Setup Ollama-specific routes
            setup_ollama_routes(app)
            logger.info("Ollama routes registered successfully")

        # Setup chat routes (chat, streaming, etc)
        register_chat_routes(app)
        logger.info("Chat routes registered successfully")

        # Setup health check and basic routes
        register_health_routes(app)
        logger.info("Health check routes registered successfully")

    except Exception as e:
        logger.error(f"Error setting up routes: {e}", exc_info=True)
        raise
