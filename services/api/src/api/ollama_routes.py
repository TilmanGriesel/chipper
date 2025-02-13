import os

from api.config import BYPASS_OLLAMA_RAG, logger
from api.middleware import require_api_key
from api.ollama_proxy import OllamaProxy


class OllamaRoutes:
    def __init__(self, app, proxy: OllamaProxy):
        self.app = app
        self.proxy = proxy
        self.register_routes()

        if BYPASS_OLLAMA_RAG:
            self.register_bypass_routes()

    def register_bypass_routes(self):
        @self.app.route("/api/chat", methods=["POST"])
        @require_api_key
        def chat():
            try:
                return self.proxy.chat()
            except Exception as e:
                logger.error(f"Error in chat endpoint: {e}")
                return {"error": "An internal error has occurred!"}, 500

    def register_routes(self):
        # Generation endpoints
        @self.app.route("/api/generate", methods=["POST"])
        @require_api_key
        def generate():
            try:
                return self.proxy.generate()
            except Exception as e:
                logger.error(f"Error in generate endpoint: {e}")
                return {"error": str(e)}, 500

        @self.app.route("/api/embeddings", methods=["POST"])
        @require_api_key
        def embeddings():
            try:
                return self.proxy.embeddings()
            except Exception as e:
                logger.error(f"Error in embeddings endpoint: {e}")
                return {"error": str(e)}, 500

        @self.app.route("/api/embed", methods=["POST"])
        @require_api_key
        def embed():
            try:
                return self.proxy.embed()
            except Exception as e:
                logger.error(f"Error in embed endpoint: {e}")
                return {"error": str(e)}, 500

        # Model management endpoints
        @self.app.route("/api/create", methods=["POST"])
        @require_api_key
        def create():
            try:
                return self.proxy.create()
            except Exception as e:
                logger.error(f"Error in create endpoint: {e}")
                return {"error": str(e)}, 500

        @self.app.route("/api/show", methods=["POST"])
        @require_api_key
        def show():
            try:
                return self.proxy.show()
            except Exception as e:
                logger.error(f"Error in show endpoint: {e}")
                return {"error": str(e)}, 500

        @self.app.route("/api/copy", methods=["POST"])
        @require_api_key
        def copy():
            try:
                return self.proxy.copy()
            except Exception as e:
                logger.error(f"Error in copy endpoint: {e}")
                return {"error": str(e)}, 500

        @self.app.route("/api/delete", methods=["DELETE"])
        @require_api_key
        def delete():
            try:
                return self.proxy.delete()
            except Exception as e:
                logger.error(f"Error in delete endpoint: {e}")
                return {"error": str(e)}, 500

        @self.app.route("/api/pull", methods=["POST"])
        @require_api_key
        def pull():
            try:
                return self.proxy.pull()
            except Exception as e:
                logger.error(f"Error in pull endpoint: {e}")
                return {"error": str(e)}, 500

        @self.app.route("/api/push", methods=["POST"])
        @require_api_key
        def push():
            try:
                return self.proxy.push()
            except Exception as e:
                logger.error(f"Error in push endpoint: {e}")
                return {"error": str(e)}, 500

        # Blob management endpoints
        @self.app.route("/api/blobs/<digest>", methods=["HEAD"])
        @require_api_key
        def check_blob(digest):
            try:
                return self.proxy.check_blob(digest)
            except Exception as e:
                logger.error(f"Error in check_blob endpoint: {e}")
                return {"error": "An internal error has occurred!"}, 500

        @self.app.route("/api/blobs/<digest>", methods=["POST"])
        @require_api_key
        def push_blob(digest):
            try:
                return self.proxy.push_blob(digest)
            except Exception as e:
                logger.error(f"Error in push_blob endpoint: {e}")
                return {"error": "An internal error has occurred!"}, 500

        # Model listing and status endpoints
        @self.app.route("/api/tags", methods=["GET"])
        @require_api_key
        def list_local_models():
            try:
                return self.proxy.list_local_models()
            except Exception as e:
                logger.error(f"Error in list_local_models endpoint: {e}")
                return {"error": "An internal error has occurred!"}, 500

        @self.app.route("/api/ps", methods=["GET"])
        @require_api_key
        def list_running_models():
            try:
                return self.proxy.list_running_models()
            except Exception as e:
                logger.error(f"Error in list_running_models endpoint: {e}")
                return {"error": "An internal error has occurred!"}, 500

        @self.app.route("/api/version", methods=["GET"])
        @require_api_key
        def version():
            try:
                return self.proxy.version()
            except Exception as e:
                logger.error(f"Error in version endpoint: {e}")
                return {"error": "An internal error has occurred!"}, 500


def setup_ollama_proxy_routes(app):
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    proxy = OllamaProxy(ollama_url)
    OllamaRoutes(app, proxy)
    logger.info(f"Initialized Ollama proxy routes with Ollama URL: {ollama_url}")
    return proxy
