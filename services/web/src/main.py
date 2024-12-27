import argparse
import hashlib
import json
import logging
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict
from urllib.parse import urljoin

from dotenv import load_dotenv
from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    send_from_directory,
    session,
)
from requests.exceptions import ConnectionError, RequestException, Timeout

load_dotenv()

# Configure Logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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

    @app.errorhandler(404)
    def not_found_error(error):
        logger.warning(f"404 error: {request.url}")
        return "", 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 error: {str(error)}")
        return "", 500

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
