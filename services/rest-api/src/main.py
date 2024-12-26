import logging
import os
import secrets
from datetime import datetime
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix

from core.query import RAGQueryPipeline

load_dotenv()

app = Flask(__name__)
CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["1000 per day", "10 per minute"],
    storage_uri="memory://",
)

API_KEY = os.getenv("WEB_API_KEY")
if not API_KEY:
    API_KEY = secrets.token_urlsafe(32)
    logger.info(f"Generated API key: {API_KEY}")


def initialize():
    rag = RAGQueryPipeline(
        es_url=os.getenv("ES_URL"),
        es_index=os.getenv("ES_INDEX"),
        ollama_url=os.getenv("OLLAMA_URL"),
        model_name=os.getenv("MODEL_NAME"),
        embedding_model=os.getenv("EMBEDDING_MODEL"),
        system_prompt=os.getenv("SYSTEM_PROMPT"),
        context_window=int(os.getenv("CONTEXT_WINDOW", 4096)),
        temperature=float(os.getenv("TEMPERATURE", 0.7)),
        seed=int(os.getenv("SEED", 0)),
        top_k=int(os.getenv("TOP_K", 5)),
    )

    result = rag.run_query(query="hello world", conversation=[], print_response=True)
    logging.info(f"Test query compled, result: {result}")


def process_query():
    try:
        data = request.get_json()
        query = data.get("query")
        es_index = data.get("es_index")
        model_name = data.get("model_name")
        conversation = data.get("conversation", [])

        rag = RAGQueryPipeline(
            es_url=os.getenv("ES_URL"),
            es_index=es_index,
            ollama_url=os.getenv("OLLAMA_URL"),
            model_name=model_name,
            embedding_model=os.getenv("EMBEDDING_MODEL"),
            system_prompt=os.getenv("SYSTEM_PROMPT"),
            context_window=int(os.getenv("CONTEXT_WINDOW", 4096)),
            temperature=float(os.getenv("TEMPERATURE", 0.7)),
            seed=int(os.getenv("SEED", 0)),
            top_k=int(os.getenv("TOP_K", 5)),
        )

        success = True
        result = None
        try:
            result = rag.run_query(
                query=query, conversation=conversation, print_response=False
            )
        except Exception as e:
            success = False

        latest_interaction = []
        if success:
            latest_interaction = [
                {
                    "role": "user",
                    "content": query,
                    "timestamp": datetime.now().isoformat(),
                },
                {
                    "role": "assistant",
                    "content": result["llm"]["replies"][0],
                    "timestamp": datetime.now().isoformat(),
                },
            ]

        return jsonify(
            {
                "success": success,
                "timestamp": datetime.now().isoformat(),
                "result": result,
                "conversation": conversation + latest_interaction,
            }
        )

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "An error occurred while processing your request",
                }
            ),
            500,
        )


def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key != API_KEY:
            return jsonify({"error": "Invalid or missing API key"}), 401
        return f(*args, **kwargs)

    return decorated_function


@app.before_request
def before_request():
    logger.info(f"Request {request.method} {request.path} from {request.remote_addr}")
    if (
        os.getenv("WEB_REQUIRE_SECURE", "False").lower() == "true"
        and not request.is_secure
    ):
        return jsonify({"error": "HTTPS required"}), 403


@app.after_request
def after_request(response):
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


@app.route("/api/query", methods=["POST"])
@require_api_key
def query_endpoint():
    return process_query()


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})


if __name__ == "__main__":
    initialize()
    app.run(
        host=os.getenv("WEB_API_HOST", "0.0.0.0"),
        port=int(os.getenv("WEB_API_PORT", "8000")),
        debug=os.getenv("WEB_DEBUG", "False").lower() == "true",
    )
