import argparse
import hashlib
import logging
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from threading import Event
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    Response,
    jsonify,
    render_template,
    request,
    session,
    stream_with_context,
)
from requests.exceptions import ConnectionError, RequestException, Timeout

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

APP_VERSION = os.getenv("APP_VERSION", "[DEV]")
BUILD_NUMBER = os.getenv("APP_BUILD_NUM", "0")


def show_welcome():
    PURPLE = "\033[34m"
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
    print(f"{CYAN}       Chipper Web {APP_VERSION}.{BUILD_NUMBER}", flush=True)
    print(f"{RESET}\n", flush=True)


show_welcome()


class SessionManager:
    def __init__(self, app):
        self.app = app
        self.abort_flags = {}
        app.secret_key = secrets.token_hex(32)
        logger.info("Initialized SessionManager with new secret key")
        app.config.update(
            SESSION_COOKIE_SECURE=False,
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SAMESITE="Lax",
            PERMANENT_SESSION_LIFETIME=timedelta(hours=24),
        )

        @app.before_request
        def validate_session():
            self._ensure_valid_session()

    def get_abort_flag(self, session_id: str) -> Event:
        if session_id not in self.abort_flags:
            self.abort_flags[session_id] = Event()
        return self.abort_flags[session_id]

    def abort_chat(self, session_id: str):
        if session_id in self.abort_flags:
            self.abort_flags[session_id].set()
            logger.info(f"Chat aborted for session {session_id[:8]}...")

    def reset_abort_flag(self, session_id: str):
        if session_id in self.abort_flags:
            self.abort_flags[session_id] = Event()
            logger.debug(f"Reset abort flag for session {session_id[:8]}...")

    def get_session(self):
        self._ensure_valid_session()
        return session

    def get_session_setting(self, key: str, default=None):
        return session.get(key, default)

    def _ensure_valid_session(self):
        if "session_id" not in session:
            logger.info("No session_id found - initializing new session")
            self._initialize_new_session()
        elif "created_at" in session:
            created_at = datetime.fromisoformat(session["created_at"])
            if datetime.now() - created_at > timedelta(hours=24):
                logger.warning(
                    f"Session expired (created: {created_at.isoformat()}) - initializing new session"
                )
                self._initialize_new_session()
            else:
                logger.debug(
                    f"Valid session found (id: {session['session_id'][:8]}...)"
                )

    def _initialize_new_session(self):
        old_session_id = session.get("session_id", "none")
        session.clear()
        new_session_id = secrets.token_urlsafe(32)
        session["session_id"] = new_session_id
        session["created_at"] = datetime.now().isoformat()
        session["messages"] = []
        logger.info(
            f"New session initialized: {old_session_id[:8]}... → {new_session_id[:8]}..."
        )

    def get_chat_messages(self) -> List[Dict]:
        self._ensure_valid_session()
        return session.get("messages", [])

    def update_chat_messages(self, role: str, content: str, max_size: int):
        messages = self.get_chat_messages()
        messages.append(
            {"role": role, "content": content, "timestamp": datetime.now().isoformat()}
        )
        if len(messages) > max_size:
            messages = messages[-max_size:]
        session["messages"] = messages

    def clear_messages(self):
        if "session_id" in session:
            session["messages"] = []

    def invalidate_session(self):
        if "session_id" in session:
            session.clear()


class AssetConfig:
    def __init__(self):
        self.asset_url = os.getenv("ASSET_URL", "/static")
        self.cache_timeout = int(os.getenv("ASSET_CACHE_TIMEOUT", "31536000"))
        self.debug_assets = os.getenv("ASSET_DEBUG", "False").lower() == "true"
        self.asset_version = os.getenv("ASSET_VERSION", self._generate_version())

    def _generate_version(self) -> str:
        return hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8]

    def get_asset_url(self, filename: str) -> str:
        if self.debug_assets:
            timestamp = datetime.now().timestamp()
            return f"{self.asset_url}/{filename}?t={timestamp}"
        return f"{self.asset_url}/{filename}?v={self.asset_version}"


class MessageType(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    ERROR = "error"


@dataclass
class Message:
    content: str
    type: MessageType
    timestamp: float = None


def make_api_request(endpoint: str, data: Dict, stream: bool = False) -> Any:
    api_url = os.getenv("API_URL", "http://localhost:8000")
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": os.getenv("API_KEY", "EXAMPLE_API_KEY"),
    }

    try:
        response = requests.post(
            f"{api_url}{endpoint}",
            headers=headers,
            json=data,
            stream=stream,
            timeout=120,
        )
        response.raise_for_status()
        return response
    except (ConnectionError, Timeout) as e:
        logger.error(f"Connection error: {str(e)}")
        raise
    except RequestException as e:
        logger.error(f"Request error: {str(e)}")
        raise


def create_app():
    app = Flask(
        __name__,
        static_url_path="/static",
        static_folder="static",
        template_folder="templates",
    )
    session_manager = SessionManager(app)
    app.config["session_manager"] = session_manager
    asset_config = AssetConfig()
    app.config["asset_config"] = asset_config

    @app.context_processor
    def inject_asset_url():
        return {
            "asset_url": asset_config.asset_url,
            "get_asset_url": asset_config.get_asset_url,
        }

    @app.route("/api/chat", methods=["POST"])
    def chat():
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Invalid JSON payload"}), 400

            session_id = session.get("session_id")
            abort_flag = session_manager.get_abort_flag(session_id)
            session_manager.reset_abort_flag(session_id)

            # streaming response
            if data.get("stream", True):
                api_response = make_api_request("/api/chat", data, stream=True)

                def generate():
                    try:
                        for chunk in api_response.iter_lines():
                            if abort_flag.is_set():
                                logger.info(
                                    f"Aborting stream for session {session_id[:8]}..."
                                )
                                api_response.close()
                                yield 'data: {"type": "abort", "content": "Request aborted"}\n\n'
                                break
                            if chunk:
                                yield chunk.decode() + "\n\n"
                    except Exception as e:
                        logger.error(f"Stream error: {str(e)}")
                        yield f'data: {{"type": "error", "content": "{str(e)}"}}\n\n'

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
                # non-streaming response
                response = make_api_request("/api/chat", data)
                return jsonify(response.json())

        except (ConnectionError, Timeout):
            return jsonify({"error": "Connection error"}), 503
        except RequestException as e:
            status_code = (
                e.response.status_code
                if hasattr(e, "response") and e.response is not None
                else 500
            )
            return jsonify({"error": str(e)}), status_code

    @app.route("/api/chat/abort", methods=["POST"])
    def abort_chat():
        try:
            session_id = session.get("session_id")
            if not session_id:
                return jsonify({"error": "No active session"}), 400

            session_manager.abort_chat(session_id)
            return jsonify({"status": "success", "message": "Chat aborted"})
        except Exception as e:
            logger.error(f"Error aborting chat: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/assets/config", methods=["GET"])
    def get_asset_config():
        return jsonify(
            {
                "assetUrl": asset_config.asset_url,
                "cacheTimeout": asset_config.cache_timeout,
                "debugMode": asset_config.debug_assets,
                "version": asset_config.asset_version,
            }
        )

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
        logger.warning(f"404 error: {request.url}")
        return "", 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 error: {str(error)}")
        return "", 500

    return app


app = create_app()


def parse_args():
    parser = argparse.ArgumentParser(description="Web Client Application")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument(
        "--host", type=str, default="127.0.0.1", help="Host to run the application on"
    )
    parser.add_argument(
        "--port", type=int, default=5000, help="Port to run the application on"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    debug_mode = os.getenv("DEBUG", str(args.debug)).lower() == "true"
    host = os.getenv("HOST", args.host)
    port = int(os.getenv("PORT", args.port))

    if debug_mode:
        app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

    logger.info(
        f"Starting web client application on {host}:{port} (debug={debug_mode})"
    )

    app.run(host=host, port=port, debug=debug_mode)
