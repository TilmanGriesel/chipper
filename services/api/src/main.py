import json
import logging
import os
import queue
import secrets
import threading
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path

import elasticsearch
from core.query import QueryPipelineConfig, RAGQueryPipeline
from dotenv import load_dotenv
from flask import Flask, Response, abort, jsonify, request, stream_with_context
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
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
    default_limits=["10000 per day", "1000 per minute"],
    storage_uri="memory://",
)

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    API_KEY = secrets.token_urlsafe(32)
    logger.info(f"Generated API key: {API_KEY}")


def load_systemprompt(base_path: str) -> str:
    file = Path(base_path) / ".systemprompt"
    default_prompt = ""

    if not file.exists():
        logger.info("No .systemprompt file found. Using default prompt.")
        return default_prompt

    try:
        with open(file, "r", encoding="utf-8") as f:
            content = f.read().strip()

        if not content:
            logger.warning("System prompt file is empty. Using default prompt.")
            return default_prompt

        logger.info(
            f"Successfully loaded system prompt from {file}; content: '{content}'"
        )
        return content

    except Exception as e:
        logger.error(f"Error reading system prompt file: {e}")
        return default_prompt


system_prompt_value = load_systemprompt(os.getenv("SYSTEM_PROMPT_PATH", os.getcwd()))


def create_pipeline_config(model: str = None, index: str = None) -> QueryPipelineConfig:
    return QueryPipelineConfig(
        es_url=os.getenv("ES_URL"),
        es_index=index or os.getenv("ES_INDEX"),
        ollama_url=os.getenv("OLLAMA_URL"),
        model_name=model or os.getenv("MODEL_NAME"),
        embedding_model=os.getenv("EMBEDDING_MODEL"),
        system_prompt=system_prompt_value,
        context_window=int(os.getenv("CONTEXT_WINDOW", 4096)),
        temperature=float(os.getenv("TEMPERATURE", 0.7)),
        seed=int(os.getenv("SEED", 0)),
        top_k=int(os.getenv("TOP_K", 5)),
    )


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
    if os.getenv("REQUIRE_SECURE", "False").lower() == "true" and not request.is_secure:
        abort(403)


@app.after_request
def after_request(response):
    response.headers.update(
        {
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
        }
    )
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

        if not messages:
            abort(400, description="No messages provided")
        query = messages[-1].get("content")
        if not query:
            abort(400, description="Invalid message format")

        conversation = messages[:-1] if len(messages) > 1 else []
        config = create_pipeline_config(model, index)

        if stream:
            return handle_streaming_response(config, query, conversation)
        else:
            return handle_standard_response(config, query, conversation, messages)

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        abort(500, description="Internal Server Error.")


def handle_streaming_response(
    config: QueryPipelineConfig, query: str, conversation: list
) -> Response:
    q = queue.Queue()

    def format_model_status(status):
        model = status.get("model", "unknown")
        status_type = status.get("status")

        if status_type == "pulling":
            return f"Starting to download model {model}..."
        elif status_type == "progress":
            percentage = int(status.get("percentage", 0))
            return f"Downloading model {model}: {percentage}% complete"
        elif status_type == "complete":
            return f"Successfully downloaded model {model}"
        elif status_type == "error" and "pull" in status.get("error", "").lower():
            error_msg = status.get("error", "Unknown error")
            return f"Error downloading model {model}: {error_msg}"

        return None

    def streaming_callback(chunk):
        if chunk.content:
            response_data = {
                "type": "chat_response",
                "chunk": chunk.content,
                "done": False,
                "full_response": None,
            }
            q.put(f"data: {json.dumps(response_data)}\n\n")

    rag = RAGQueryPipeline(config=config, streaming_callback=streaming_callback)

    def run_rag():
        try:
            for status in rag.initialize_and_check_models():
                message = format_model_status(status)
                if message:
                    response_data = {
                        "type": "chat_response",
                        "chunk": message + "\n",
                        "done": False,
                        "full_response": None,
                    }
                    q.put(f"data: {json.dumps(response_data)}\n\n")

            rag.create_query_pipeline()
            result = rag.run_query(
                query=query, conversation=conversation, print_response=False
            )
            final_data = {
                "type": "chat_response",
                "chunk": "",
                "done": True,
                "full_response": result,
            }
            q.put(f"data: {json.dumps(final_data)}\n\n")
        except elasticsearch.BadRequestError:
            error_data = {
                "type": "chat_response",
                "chunk": "Error: Embedding retriever error. Index not found.\n",
                "done": True,
            }
            q.put(f"data: {json.dumps(error_data)}\n\n")
        except Exception as e:
            error_data = {
                "type": "chat_response",
                "chunk": f"Error: {str(e)}\n",
                "done": True,
            }
            logger.error(f"Error in RAG pipeline: {e}", exc_info=True)
            q.put(f"data: {json.dumps(error_data)}\n\n")

    thread = threading.Thread(target=run_rag, daemon=True)
    thread.start()

    def generate():
        while True:
            try:
                data_item = q.get(timeout=120)
                yield data_item

                json_data = json.loads(data_item.replace("data: ", "").strip())
                if json_data.get("done") is True:
                    logger.info("Streaming completed.")
                    break

            except queue.Empty:
                yield "event: heartbeat\ndata: {}\n\n"
                logger.warning("Queue timeout. Sending heartbeat.")
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e} | Data: {data_item}")
                error_message = {
                    "type": "error",
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


def handle_standard_response(
    config: QueryPipelineConfig, query: str, conversation: list, messages: list
) -> Response:
    rag = RAGQueryPipeline(config=config)

    success = True
    result = None
    try:
        result = rag.run_query(
            query=query, conversation=conversation, print_response=False
        )
    except Exception as e:
        success = False
        logger.error(f"Error in RAG pipeline: {e}", exc_info=True)

    if success and result:
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


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify(
        {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}
    )


@app.errorhandler(404)
def not_found_error(error):
    return "", 404


if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        debug=os.getenv("DEBUG", "False").lower() == "true",
    )
