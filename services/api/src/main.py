import json
import logging
import os
import queue
import secrets
import threading
from datetime import datetime
from functools import wraps

from core.query import RAGQueryPipeline
from dotenv import load_dotenv
from flask import Flask, Response, abort, jsonify, request, stream_with_context
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from haystack.dataclasses import StreamingChunk
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv()

app = Flask(__name__)
CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["1000 per day", "1000 per minute"],
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


def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key != API_KEY:
            abort(401)
        return f(*args, **kwargs)

    return decorated_function


@app.before_request
def before_request():
    logger.info(f"Request {request.method} {request.path} from {request.remote_addr}")
    if (
        os.getenv("WEB_REQUIRE_SECURE", "False").lower() == "true"
        and not request.is_secure
    ):
        abort(403)


@app.after_request
def after_request(response):
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


@app.route("/api/chat", methods=["POST"])
@require_api_key
def chat():
    try:
        data = request.get_json()
        if not data:
            logger.error("No JSON payload received.")
            abort(400, description="Invalid JSON payload.")

        model = data.get("model")
        messages = data.get("messages", [])
        stream = data.get("stream", True)
        options = data.get("options", {})
        index = options.get("index")

        if index is None or "":
            index = os.getenv("ES_INDEX")

        if model is None or "":
            model = os.getenv("MODEL_NAME")

        if not model or not index:
            logger.error("Missing required fields in the request.")
            abort(400, description="Missing required fields: 'model', 'index'")

        if not messages:
            abort(400, description="No messages provided")
        query = messages[-1].get("content")
        if not query:
            abort(400, description="Invalid message format")

        conversation = messages[:-1] if len(messages) > 1 else []

        if stream:
            q = queue.Queue()

            def streaming_callback(chunk):
                if chunk.content:
                    response_data = {
                        "chunk": chunk.content,
                        "done": False,
                        "full_response": None,
                    }
                    q.put(f"data: {json.dumps(response_data)}\n\n")

            rag = RAGQueryPipeline(
                es_url=os.getenv("ES_URL"),
                es_index=index,
                ollama_url=os.getenv("OLLAMA_URL"),
                model_name=model,
                embedding_model=os.getenv("EMBEDDING_MODEL"),
                system_prompt=os.getenv("SYSTEM_PROMPT"),
                context_window=int(os.getenv("CONTEXT_WINDOW", 4096)),
                temperature=float(os.getenv("TEMPERATURE", 0.7)),
                seed=int(os.getenv("SEED", 0)),
                top_k=int(os.getenv("TOP_K", 5)),
                streaming_callback=streaming_callback,
            )

            def run_rag():
                try:
                    rag.create_query_pipeline()
                    result = rag.run_query(
                        query=query, conversation=conversation, print_response=False
                    )
                    final_data = {"chunk": "", "done": True, "full_response": result}
                    q.put(f"data: {json.dumps(final_data)}\n\n")
                except Exception as e:
                    error_data = {"error": str(e), "done": True}
                    logger.error(f"Error in RAG pipeline: {e}", exc_info=True)
                    q.put(f"data: {json.dumps(error_data)}\n\n")

            thread = threading.Thread(target=run_rag, daemon=True)
            thread.start()

            def generate():
                while True:
                    try:
                        data = q.get(timeout=30)
                        yield data

                        json_data = json.loads(data.replace("data: ", "").strip())
                        if json_data.get("done") is True:
                            logger.info("Streaming completed.")
                            break

                    except queue.Empty:
                        heartbeat = "event: heartbeat\ndata: {}\n\n"
                        yield heartbeat
                        logger.warning("Queue timeout. Sending heartbeat.")
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error: {e} | Data: {data}")
                        error_message = {
                            "error": "Invalid JSON format received.",
                            "done": True,
                        }
                        yield f"data: {json.dumps(error_message)}\n\n"
                        break

            return Response(
                stream_with_context(generate()),
                mimetype="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "X-Accel-Buffering": "no",
                    "Connection": "keep-alive",
                },
            )

        else:
            # Non-streaming response
            rag = RAGQueryPipeline(
                es_url=os.getenv("ES_URL"),
                es_index=index,
                ollama_url=os.getenv("OLLAMA_URL"),
                model_name=model,
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
                logger.error(f"Error in RAG pipeline: {e}", exc_info=True)

            if success:
                latest_message = {
                    "role": "assistant",
                    "content": result["llm"]["replies"][0],
                    "timestamp": datetime.now().isoformat(),
                }
                messages.append(latest_message)

            return jsonify(
                {
                    "success": success,
                    "timestamp": datetime.now().isoformat(),
                    "result": result,
                    "messages": messages,
                }
            )

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        abort(500, description="Internal Server Error.")


@app.route("/", methods=["GET"])
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})


@app.errorhandler(404)
def not_found_error(error):
    return "", 404


if __name__ == "__main__":
    initialize()
    app.run(
        host=os.getenv("WEB_API_HOST", "0.0.0.0"),
        port=int(os.getenv("WEB_API_PORT", "8000")),
        debug=os.getenv("WEB_DEBUG", "False").lower() == "true",
    )
