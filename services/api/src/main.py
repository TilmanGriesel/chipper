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
from core.pipeline_config import ModelProvider, QueryPipelineConfig
from core.rag_pipeline import RAGQueryPipeline
from dotenv import load_dotenv
from flask import Flask, Response, abort, jsonify, request, stream_with_context
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv()

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

APP_VERSION = os.getenv("APP_VERSION", "[DEV]")
BUILD_NUMBER = os.getenv("APP_BUILD_NUM", "0")

ALLOW_MODEL_CHANGE = os.getenv("ALLOW_MODEL_CHANGE", "true").lower() == "true"
ALLOW_INDEX_CHANGE = os.getenv("ALLOW_INDEX_CHANGE", "true").lower() == "true"

DAILY_LIMIT = int(os.getenv("DAILY_RATE_LIMIT", "86400"))
MINUTE_LIMIT = int(os.getenv("MINUTE_RATE_LIMIT", "60"))
STORAGE_URI = os.getenv("RATE_LIMIT_STORAGE", "memory://")


def show_welcome():
    PURPLE = "\033[35m"
    CYAN = "\033[36m"
    RESET = "\033[0m"

    print("\n", flush=True)
    print(f"{PURPLE}", flush=True)
    print("        __    _                      ", flush=True)
    print("  _____/ /_  (_)___  ____  ___  _____", flush=True)
    print(" / ___/ __ \\/ / __ \\/ __ \\/ _ \\/ ___/", flush=True)
    print("/ /__/ / / / / /_/ / /_/ /  __/ /    ", flush=True)
    print("\\___/_/ /_/_/ .___/ .___/\\___/_/     ", flush=True)
    print("           /_/   /_/                 ", flush=True)
    print(f"{RESET}", flush=True)
    print(f"{CYAN}       Chipper API {APP_VERSION}.{BUILD_NUMBER}", flush=True)
    print(f"{RESET}\n", flush=True)


show_welcome()

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[f"{DAILY_LIMIT} per day", f"{MINUTE_LIMIT} per minute"],
    storage_uri=STORAGE_URI,
)

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    API_KEY = secrets.token_urlsafe(32)
    logger.info(f"Generated API key: {API_KEY}")


def load_systemprompt(base_path: str) -> str:
    default_prompt = ""

    # Use environment variable if available
    env_var_name = "SYSTEM_PROMPT"
    env_prompt = os.getenv(env_var_name)
    if env_prompt is not None:
        content = env_prompt.strip()
        logger.info(
            f"Using system prompt from '{env_var_name}' environment variable; content: '{content}'"
        )
        return content

    # Try reading from file
    file = Path(base_path) / ".systemprompt"

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


def get_env_param(param_name, converter=None, default=None):
    value = os.getenv(param_name)
    if value is None:
        return None

    if converter is not None:
        try:
            if default is not None and value == "":
                return converter(default)
            return converter(value)
        except (ValueError, TypeError):
            return None
    return value


def create_pipeline_config(model: str = None, index: str = None) -> QueryPipelineConfig:
    provider_name = os.getenv("PROVIDER", "ollama")
    provider = (
        ModelProvider.HUGGINGFACE
        if provider_name.lower() == "hf"
        else ModelProvider.OLLAMA
    )

    if provider == ModelProvider.HUGGINGFACE:
        model_name = model or os.getenv("HF_MODEL_NAME")
        embedding_model = os.getenv("HF_EMBEDDING_MODEL_NAME")
    else:
        model_name = model or os.getenv("MODEL_NAME")
        embedding_model = os.getenv("EMBEDDING_MODEL_NAME")

    config_params = {
        "provider": provider,
        "embedding_model": embedding_model,
        "model_name": model_name,
        "system_prompt": system_prompt_value,
    }

    # Provider specific parameters
    if provider == ModelProvider.HUGGINGFACE:
        if (hf_key := os.getenv("HF_API_KEY")) is not None:
            config_params["hf_api_key"] = hf_key
    else:
        if (ollama_url := os.getenv("OLLAMA_URL")) is not None:
            config_params["ollama_url"] = ollama_url

    # Model pull configuration
    allow_pull = os.getenv("ALLOW_MODEL_PULL")
    if allow_pull is not None:
        config_params["allow_model_pull"] = allow_pull.lower() == "true"

    # Core generation parameters
    if (context_window := get_env_param("CONTEXT_WINDOW", int, "8192")) is not None:
        config_params["context_window"] = context_window

    for param in ["TEMPERATURE", "SEED", "TOP_K"]:
        if (
            value := get_env_param(param, float if param == "TEMPERATURE" else int)
        ) is not None:
            config_params[param.lower()] = value

    # Advanced sampling parameters
    for param in ["TOP_P", "MIN_P"]:
        if (value := get_env_param(param, float)) is not None:
            config_params[param.lower()] = value

    # Mirostat parameters
    if (mirostat := get_env_param("MIROSTAT", int)) is not None:
        config_params["mirostat"] = mirostat
        # Only add eta and tau if mirostat is defined
        for param in ["MIROSTAT_ETA", "MIROSTAT_TAU"]:
            if (value := get_env_param(param, float)) is not None:
                config_params[param.lower()] = value

    # Repetition control parameters
    for param in ["REPEAT_LAST_N", "REPEAT_PENALTY"]:
        if (
            value := get_env_param(param, int if param == "REPEAT_LAST_N" else float)
        ) is not None:
            config_params[param.lower()] = value

    # Generation control parameters
    if (num_predict := get_env_param("NUM_PREDICT", int)) is not None:
        config_params["num_predict"] = num_predict

    if (tfs_z := get_env_param("TFS_Z", float)) is not None:
        config_params["tfs_z"] = tfs_z

    if (stop := os.getenv("STOP")) is not None:
        config_params["stop_sequence"] = stop

    # Elasticsearch parameters
    if (es_url := os.getenv("ES_URL")) is not None:
        config_params["es_url"] = es_url

        if index is not None:
            config_params["es_index"] = index
        elif (es_index := os.getenv("ES_INDEX")) is not None:
            config_params["es_index"] = es_index

        if (es_top_k := get_env_param("ES_TOP_K", int, "5")) is not None:
            config_params["es_top_k"] = es_top_k

        if (
            es_num_candidates := get_env_param("ES_NUM_CANDIDATES", int, "-1")
        ) is not None:
            config_params["es_num_candidates"] = es_num_candidates

        if (es_user := os.getenv("ES_BASIC_AUTH_USERNAME")) is not None:
            config_params["es_basic_auth_user"] = es_user

        if (es_pass := os.getenv("ES_BASIC_AUTH_PASSWORD")) is not None:
            config_params["es_basic_auth_password"] = es_pass

    # Conversation analysis and logging
    if (enable_conversation_logs := os.getenv("ENABLE_CONVERSATION_LOGS")) is not None:
        config_params["enable_conversation_logs"] = enable_conversation_logs

    return QueryPipelineConfig(**config_params)


def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        require_api_key = os.getenv("REQUIRE_API_KEY")
        if not require_api_key:
            return f(*args, **kwargs)

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

        messages = data.get("messages", [])
        if not messages:
            abort(400, description="No messages provided")

        query = messages[-1].get("content")
        if not query:
            abort(400, description="Invalid message format")

        model = data.get("model")
        if model and not ALLOW_MODEL_CHANGE:
            abort(403, description="Model changes are not allowed")

        options = data.get("options", {})
        index = options.get("index")
        if index and not ALLOW_INDEX_CHANGE:
            abort(403, description="Index changes are not allowed")

        config = create_pipeline_config(model, index)
        stream = data.get("stream", True)
        conversation = messages[:-1] if len(messages) > 1 else []
        if stream:
            return handle_streaming_response(config, query, conversation)
        else:
            return handle_standard_response(config, query, conversation)

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

        allow_model_pull = os.getenv("ALLOW_MODEL_PULL", "True").lower() == "true"
        if not allow_model_pull:
            return None

        if status_type == "pulling":
            return f"Starting to download model {model}..."
        elif status_type == "progress":
            percentage = status.get("percentage", 0)
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
        except elasticsearch.BadRequestError as e:
            error_data = {
                "type": "chat_response",
                "chunk": f"Error: Embedding retriever error. {str(e)}.\n",
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
    config: QueryPipelineConfig, query: str, conversation: list
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
        conversation.append(latest_message)

    return jsonify(
        {
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "result": result,
            "messages": conversation,
        }
    )

@app.route("/", methods=["GET"])
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify(
        {
            "service": "chipper-api",
            "version": APP_VERSION,
            "build": BUILD_NUMBER,
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
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
