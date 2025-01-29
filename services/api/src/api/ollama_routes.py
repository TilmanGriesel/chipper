import os

from api.config import logger
from api.middleware import require_api_key
from api.ollama_proxy import OllamaProxy


class OllamaRoutes:
    def __init__(self, app, proxy: OllamaProxy):
        self.app = app
        self.proxy = proxy
        self.register_routes()

    def register_routes(self):
        @self.app.route("/api/generate", methods=["POST"])
        @require_api_key
        def generate():
            try:
                return self.proxy.generate()
            except Exception as e:
                logger.error(f"Error in generate endpoint: {e}")
                return {"error": str(e)}, 500

        @self.app.route("/api/tags", methods=["GET"])
        @require_api_key
        def tags():
            try:
                return self.proxy.tags()
            except Exception as e:
                logger.error(f"Error in tags endpoint: {e}")
                return {"error": str(e)}, 500

        @self.app.route("/api/pull", methods=["POST"])
        @require_api_key
        def pull():
            try:
                return self.proxy.pull()
            except Exception as e:
                logger.error(f"Error in pull endpoint: {e}")
                return {"error": str(e)}, 500


def setup_ollama_routes(app):
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    proxy = OllamaProxy(ollama_url)
    OllamaRoutes(app, proxy)
    logger.info(f"Initialized Ollama routes with URL: {ollama_url}")
    return proxy
