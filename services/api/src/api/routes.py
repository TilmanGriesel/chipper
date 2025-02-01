import json
from datetime import datetime, timezone

from api.config import (
    ALLOW_INDEX_CHANGE,
    ALLOW_MODEL_CHANGE,
    ALLOW_MODEL_PARAMETER_CHANGE,
    APP_VERSION,
    BUILD_NUMBER,
    DEBUG,
    IGNORE_MODEL_REQUEST,
    logger,
)
from api.handlers import handle_standard_response, handle_streaming_response
from api.middleware import require_api_key
from api.pipeline_config import create_pipeline_config
from flask import Flask, Response, abort, jsonify, request


def log_request_info(request):
    request_info = {
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": {
            "endpoint": request.endpoint,
            "method": request.method,
            "remote_addr": request.remote_addr,
            "path": request.path,
        },
        "headers": dict(request.headers),
        "params": {
            "url": dict(request.args) if request.args else None,
            "form": dict(request.form) if request.form else None,
            "cookies": dict(request.cookies) if request.cookies else None,
        },
    }

    if request.data:
        content_type = request.headers.get("Content-Type", "")
        if "application/json" in content_type:
            try:
                request_info["body"] = request.get_json()
            except Exception as e:
                request_info["body"] = {
                    "error": f"Failed to parse JSON body: {str(e)}",
                    "raw": request.data.decode("utf-8", errors="replace"),
                }
        else:
            request_info["body"] = request.data.decode("utf-8", errors="replace")

    logger.info("Request: %s", json.dumps(request_info, indent=None, sort_keys=True))


def register_rag_chat_route(app: Flask):
    @app.route("/api/chat", methods=["POST"])
    @require_api_key
    def chat():
        try:
            if DEBUG:
                log_request_info(request)

            data = request.get_json()

            if not data:
                logger.error("No JSON payload received.")
                abort(400, description="Invalid JSON payload.")

            messages = data.get("messages", [])
            if not messages:
                abort(400, description="No messages provided")

            model = None
            if not IGNORE_MODEL_REQUEST:
                model = data.get("model")
                if model and not ALLOW_MODEL_CHANGE:
                    abort(403, description="Model changes are not allowed")

            # Validate message format
            for message in messages:
                if (
                    not isinstance(message, dict)
                    or "role" not in message
                    or "content" not in message
                ):
                    abort(400, description="Invalid message format")
                if message["role"] != "" and message["role"] not in [
                    "system",
                    "user",
                    "assistant",
                    "tool",
                ]:
                    abort(400, description="Invalid message role")

            # Optional parameters
            # tools = data.get("tools", [])
            # format_param = data.get("format")
            # keep_alive = data.get("keep_alive", "5m")
            options = data.get("options", {})
            stream = data.get("stream", True)

            temperature = None
            top_k = None
            top_p = None
            seed = None

            if ALLOW_MODEL_PARAMETER_CHANGE:
                temperature = data.get("temperature", None)
                top_k = data.get("top_k", None)
                top_p = data.get("top_p", None)
                seed = data.get("seed", None)

            # Handle index parameter
            index = options.get("index")
            if index and not ALLOW_INDEX_CHANGE:
                abort(403, description="Index changes are not allowed")

            # Handle images in messages
            for message in messages:
                if "images" in message and not isinstance(message["images"], list):
                    abort(400, description="Images must be provided as a list")

            # Create configuration
            config = create_pipeline_config(
                model=model,
                index=index,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                seed=seed,
            )

            # Get the latest message with content
            query = None
            for message in reversed(messages):
                content = message.get("content")
                if content:
                    query = content
                    break

            if not query:
                abort(400, description="No message with content found")

            # Handle conversation context
            conversation = messages[:-1] if len(messages) > 1 else []

            # Handle streaming vs non-streaming response
            if stream:
                return handle_streaming_response(config, query, conversation)
            else:
                return handle_standard_response(config, query, conversation)

        except Exception as e:
            logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
            abort(500, description="Internal Server Error.")


def register_health_routes(app: Flask):
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

    @app.route("/", methods=["GET"])
    def root():
        return Response("Chipper is running", mimetype="text/plain")

    @app.errorhandler(404)
    def not_found_error(error):
        return "", 404
