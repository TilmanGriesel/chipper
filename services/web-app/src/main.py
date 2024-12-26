import hashlib
import logging
import os
import argparse
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, List
from urllib.parse import urljoin

import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session, send_from_directory
from requests.exceptions import ConnectionError, Timeout, RequestException

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CommandManager:
    def __init__(self, session_manager):
        self.session_manager = session_manager
        self.commands = {
            "/help": {
                "description": "List all available commands",
                "handler": self.handle_help,
            },
            "/index": {
                "description": "Set index name",
                "usage": "/index <index_name>",
                "handler": self.handle_set_index,
            },
            "/model": {
                "description": "Set model name",
                "usage": "/model <model_name>",
                "handler": self.handle_set_model,
            },
            "/clear": {
                "description": "Clear chat history",
                "handler": self.handle_clear,
            },
        }

    def handle_command(self, message: str) -> dict:
        if not message.startswith("/"):
            return None
        command_parts = message.split()
        command = command_parts[0].lower()
        args = command_parts[1:] if len(command_parts) > 1 else []
        if command not in self.commands:
            return {
                "error": f"Unknown command: {command}",
                "suggestion": "Use /help to see available commands",
            }
        return self.commands[command]["handler"](args)

    def handle_help(self, args) -> dict:
        help_text = ["Available commands:"]
        for cmd, info in self.commands.items():
            cmd_help = f"{cmd}: {info['description']}"
            if "usage" in info:
                cmd_help += f"\n   Usage: {info['usage']}"
            help_text.append(cmd_help)
        return {"replies": ["\n".join(help_text)], "command_response": True}

    def handle_set_index(self, args) -> dict:
        if not args:
            return {
                "error": "Index name is required",
                "usage": self.commands["/set_index"]["usage"],
            }
        index_name = args[0]
        session = self.session_manager.get_session()
        session["es_index"] = index_name
        return {
            "replies": [f"Thebes index set to: {index_name}"],
            "command_response": True,
        }

    def handle_set_model(self, args) -> dict:
        if not args:
            return {
                "error": "Model name is required",
                "usage": self.commands["/set_model"]["usage"],
            }
        model_name = args[0]
        session = self.session_manager.get_session()
        session["model_name"] = model_name
        return {
            "replies": [f"Model name set to: {model_name}"],
            "command_response": True,
        }

    def handle_clear(self, args) -> dict:
        session = self.session_manager.get_session()
        self.session_manager.clear_context()
        return {"replies": ["Chat history cleared."], "command_response": True}


class SessionManager:
    def __init__(self, app):
        self.app = app
        app.secret_key = secrets.token_hex(32)
        logger.info(f"Initialized SessionManager with new secret key")
        app.config.update(
            SESSION_COOKIE_SECURE=False,
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SAMESITE="Lax",
            PERMANENT_SESSION_LIFETIME=timedelta(hours=24),
        )

        @app.before_request
        def validate_session():
            self._ensure_valid_session()

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
        session["context"] = []
        logger.info(
            f"New session initialized: {old_session_id[:8]}... → {new_session_id[:8]}..."
        )

    def get_chat_context(self) -> list:
        self._ensure_valid_session()
        return session.get("context", [])

    def update_chat_context(self, role: str, content: str, max_size: int):
        context = self.get_chat_context()
        context.append(
            {"role": role, "content": content, "timestamp": datetime.now().isoformat()}
        )
        if len(context) > max_size:
            context = context[-max_size:]
        session["context"] = context

    def clear_context(self):
        if "session_id" in session:
            session["context"] = []

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
    ASSISTANT = "chipper"
    SYSTEM = "system"
    ERROR = "error"


@dataclass
class Message:
    content: str
    type: MessageType
    timestamp: float = None


class APIError(Exception):
    pass


class Config:
    def __init__(self):
        self.base_url = f"http://{os.getenv('WEB_API_HOST', '127.0.0.1')}:{os.getenv('WEB_API_PORT', '8000')}"
        self.api_key = os.getenv("WEB_API_KEY")
        self.timeout = int(os.getenv("WEB_API_TIMEOUT", "120"))
        self.verify_ssl = os.getenv("WEB_REQUIRE_SECURE", "True").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.max_context_size = int(os.getenv("WEB_CLIENT_MAX_CONTEXT_SIZE", "20"))
        self.enable_caching = (
            os.getenv("WEB_CLIENT_ENABLE_RESPONSE_CACHE", "False").lower() == "true"
        )
        self.cache_timeout = int(os.getenv("WEB_CLIENT_RESPONSE_CACHE_TIMEOUT", "300"))
        if not self.api_key:
            raise ValueError(
                "API key must be provided through WEB_API_KEY environment variable"
            )
        logging.getLogger().setLevel(getattr(logging, self.log_level.upper()))


class APIClient:
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update(
            {"X-API-Key": config.api_key, "Content-Type": "application/json"}
        )

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = urljoin(self.config.base_url, endpoint)
        kwargs.setdefault("verify", self.config.verify_ssl)
        kwargs.setdefault("timeout", self.config.timeout)
        try:
            self.logger.debug(f"Making {method} request to {url}")
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except ConnectionError as e:
            self.logger.error(f"Connection failed: {str(e)}")
            self.logger.debug(
                f"Connection details: host={self.config.base_url}, timeout={self.config.timeout}"
            )
            raise APIError(f"Failed to connect to API service: {str(e)}")
        except Timeout as e:
            self.logger.error(f"Request timed out: {str(e)}")
            raise APIError(f"API request timed out after {self.config.timeout} seconds")
        except RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            raise APIError(f"API request failed: {str(e)}")

    def query(
        self,
        query_text: str,
        conversation_context: List[Dict[str, str]],
        es_index: str = None,
        model_name: str = None,
    ) -> Dict[str, Any]:
        payload = {"query": query_text, "conversation": conversation_context}
        if es_index:
            payload["es_index"] = es_index
        if model_name:
            payload["model_name"] = model_name
        return self._make_request("POST", "/api/query", json=payload)

    def health_check(self) -> Dict[str, Any]:
        return self._make_request("GET", "/health")


def create_app():
    app = Flask(
        __name__,
        static_url_path="/static",
        static_folder="static",
        template_folder="templates",
    )
    session_manager = SessionManager(app)
    app.config["session_manager"] = session_manager
    command_manager = CommandManager(session_manager)
    app.config["command_manager"] = command_manager
    asset_config = AssetConfig()
    app.config["asset_config"] = asset_config

    @app.context_processor
    def inject_asset_url():
        return {
            "asset_url": asset_config.asset_url,
            "get_asset_url": asset_config.get_asset_url,
        }

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/chat", methods=["POST"])
    def chat():
        try:
            session_manager = app.config["session_manager"]
            command_manager = app.config["command_manager"]
            user_message = request.json.get("message", "")
            if not user_message:
                logger.warning(
                    f"Empty message received (session: {session.get('session_id', 'unknown')[:8]}...)"
                )
                return jsonify({"error": "Message is required"}), 400
            command_response = command_manager.handle_command(user_message)
            if command_response is not None:
                if "error" in command_response:
                    return jsonify(command_response), 400
                return jsonify(
                    {
                        "replies": command_response["replies"],
                        "timestamp": datetime.now().isoformat(),
                        "session_id": session.get("session_id"),
                        "command_response": True,
                    }
                )
            config = Config()
            context = session_manager.get_chat_context()
            client = APIClient(config)
            es_index = session_manager.get_session_setting("es_index")
            model_name = session_manager.get_session_setting("model_name")
            try:
                logger.info(
                    f"Processing chat request (session: {session['session_id'][:8]}..., "
                    f"context size: {len(context)}, index: {es_index}, model: {model_name})"
                )
                response = client.query(
                    user_message, context, es_index=es_index, model_name=model_name
                )
            except APIError as e:
                logger.error(
                    f"API query failed (session: {session['session_id'][:8]}...): {str(e)}"
                )
                return (
                    jsonify(
                        {
                            "error": "Failed to get response from API service",
                            "details": str(e),
                        }
                    ),
                    503,
                )
            replies = (
                response.get("result", {})
                .get("llm", {})
                .get("replies", ["No response received"])
            )
            logger.info(
                f"Received {len(replies)} replies from API (session: {session['session_id'][:8]}...)"
            )
            session_manager.update_chat_context(
                "user", user_message, config.max_context_size
            )
            for reply in replies:
                session_manager.update_chat_context(
                    "chipper", reply, config.max_context_size
                )
            return jsonify(
                {
                    "replies": replies,
                    "timestamp": datetime.now().isoformat(),
                    "session_id": session.get("session_id"),
                }
            )
        except Exception as e:
            session_id = session.get("session_id", "unknown")
            logger.exception(
                f"Unexpected chat error (session: {session_id[:8]}...): {str(e)}"
            )
            return (
                jsonify({"error": "An unexpected error occurred", "details": str(e)}),
                500,
            )

    @app.route("/api/clear", methods=["POST"])
    def clear_context():
        try:
            session_manager = app.config["session_manager"]
            session_manager.clear_context()
            logger.info(
                f"Context cleared via API (session: {session.get('session_id', 'unknown')[:8]}...)"
            )
            return jsonify({"status": "success"})
        except Exception as e:
            logger.error(
                f"Failed to clear context (session: {session.get('session_id', 'unknown')[:8]}...): {str(e)}"
            )
            return jsonify({"error": str(e)}), 500

    @app.route("/api/context-size", methods=["POST"])
    def update_context_size():
        try:
            new_size = int(request.json.get("size", 10))
            if new_size < 1:
                logger.warning(f"Invalid context size requested: {new_size}")
                return jsonify({"error": "Context size must be positive"}), 400
            session_manager = app.config["session_manager"]
            context = session_manager.get_chat_context()
            if len(context) > new_size:
                context = context[-new_size:]
            session["context"] = context
            logger.info(
                f"Updated context size to: {new_size} (session: {session.get('session_id', 'unknown')[:8]}...)"
            )
            return jsonify({"status": "success", "new_size": new_size})
        except ValueError as e:
            logger.error(f"Invalid context size value: {str(e)}")
            return jsonify({"error": "Invalid context size"}), 400

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
    def local_health():
        try:
            config = Config()
            client = APIClient(config)
            api_health = client.health_check()
            return jsonify(
                {
                    "status": "healthy",
                    "api_status": api_health,
                    "config": {
                        "host": config.base_url,
                        "timeout": config.timeout,
                        "verify_ssl": config.verify_ssl,
                        "max_context_size": config.max_context_size,
                        "enable_caching": config.enable_caching,
                        "cache_timeout": config.cache_timeout,
                    },
                    "asset_config": {
                        "asset_url": asset_config.asset_url,
                        "cache_timeout": asset_config.cache_timeout,
                        "debug_mode": asset_config.debug_assets,
                        "version": asset_config.asset_version,
                    },
                }
            )
        except Exception as e:
            logger.exception("Health check failed")
            return jsonify({"status": "unhealthy", "error": str(e)}), 503

    @app.errorhandler(404)
    def not_found_error(error):
        logger.warning(f"404 error: {request.url}")
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 error: {str(error)}")
        return jsonify({"error": "Internal server error"}), 500

    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        uploads_dir = os.path.join(app.root_path, "uploads")
        return send_from_directory(uploads_dir, filename)

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

    debug_mode = os.getenv("WEB_CLIENT_DEBUG", str(args.debug)).lower() == "true"
    host = os.getenv("WEB_CLIENT_HOST", args.host)
    port = int(os.getenv("WEB_CLIENT_PORT", args.port))

    if debug_mode:
        app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

    logger.info(
        f"Starting web client application on {host}:{port} (debug={debug_mode})"
    )

    app.run(host=host, port=port, debug=debug_mode)
