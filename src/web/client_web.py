import hashlib
import logging
import os
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
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
            SESSION_COOKIE_SAMESITE='Lax',
            PERMANENT_SESSION_LIFETIME=timedelta(hours=24)
        )
        logger.debug("Configured secure session settings")

        @app.before_request
        def validate_session():
            self._ensure_valid_session()

    def _ensure_valid_session(self):
        if 'session_id' not in session:
            logger.info("No session_id found - initializing new session")
            self._initialize_new_session()
        elif 'created_at' in session:
            created_at = datetime.fromisoformat(session['created_at'])
            if datetime.now() - created_at > timedelta(hours=24):
                logger.warning(f"Session expired (created: {created_at.isoformat()}) - initializing new session")
                self._initialize_new_session()
            else:
                logger.debug(f"Valid session found (id: {session['session_id'][:8]}...)")

    def _initialize_new_session(self):
        old_session_id = session.get('session_id', 'none')
        session.clear()
        new_session_id = secrets.token_urlsafe(32)
        session['session_id'] = new_session_id
        session['created_at'] = datetime.now().isoformat()
        session['context'] = []
        logger.info(f"New session initialized: {old_session_id[:8]}... → {new_session_id[:8]}...")

    def get_chat_context(self) -> list:
        self._ensure_valid_session()
        context_size = len(session.get('context', []))
        logger.debug(f"Retrieved chat context (session: {session['session_id'][:8]}..., size: {context_size})")
        return session.get('context', [])

    def update_chat_context(self, role: str, content: str, max_size: int):
        context = self.get_chat_context()
        context.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

        if len(context) > max_size:
            removed = len(context) - max_size
            context = context[-max_size:]
            logger.info(f"Trimmed context by {removed} messages (session: {session['session_id'][:8]}...)")

        session['context'] = context
        logger.debug(f"Updated context - new size: {len(context)} (session: {session['session_id'][:8]}...)")

    def clear_context(self):
        if 'session_id' in session:
            context_size = len(session.get('context', []))
            session['context'] = []
            logger.info(f"Cleared context of {context_size} messages (session: {session['session_id'][:8]}...)")

    def invalidate_session(self):
        if 'session_id' in session:
            session_id = session['session_id']
            session.clear()
            logger.warning(f"Session invalidated: {session_id[:8]}...")


class AssetConfig:
    def __init__(self):
        self.asset_url = os.getenv('ASSET_URL', '/static')
        self.cache_timeout = int(os.getenv('ASSET_CACHE_TIMEOUT', '31536000'))
        self.debug_assets = os.getenv('ASSET_DEBUG', 'False').lower() == 'true'
        self.asset_version = os.getenv('ASSET_VERSION', self._generate_version())

    def _generate_version(self) -> str:
        return hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8]

    def get_asset_url(self, filename: str) -> str:
        if self.debug_assets:
            timestamp = datetime.now().timestamp()
            return f"{self.asset_url}/{filename}?t={timestamp}"
        return f"{self.asset_url}/{filename}?v={self.asset_version}"


class MessageType(Enum):
    USER = "user"
    ASSISTANT = "Chipper"
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
        self.base_url = f"http://{os.getenv('WEB_HOST', '127.0.0.1')}:{os.getenv('WEB_PORT', '8001')}"
        self.api_key = os.getenv('WEB_API_KEY')
        self.timeout = int(os.getenv('API_TIMEOUT', '120'))
        self.verify_ssl = os.getenv('WEB_REQUIRE_SECURE', 'False').lower() == 'true'
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.max_context_size = int(os.getenv('MAX_CONTEXT_SIZE', '20'))
        self.enable_caching = os.getenv('ENABLE_RESPONSE_CACHE', 'False').lower() == 'true'
        self.cache_timeout = int(os.getenv('RESPONSE_CACHE_TIMEOUT', '300'))

        if not self.api_key:
            raise ValueError("API key must be provided through WEB_API_KEY environment variable")

        logging.getLogger().setLevel(getattr(logging, self.log_level.upper()))


class APIClient:
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': config.api_key,
            'Content-Type': 'application/json'
        })

    def _make_request(
            self,
            method: str,
            endpoint: str,
            **kwargs
    ) -> Dict[str, Any]:
        url = urljoin(self.config.base_url, endpoint)
        kwargs.setdefault('verify', self.config.verify_ssl)
        kwargs.setdefault('timeout', self.config.timeout)

        try:
            self.logger.debug(f"Making {method} request to {url}")
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except ConnectionError as e:
            self.logger.error(f"Connection failed: {str(e)}")
            self.logger.debug(f"Connection details: host={self.config.base_url}, timeout={self.config.timeout}")
            raise APIError(f"Failed to connect to API service: {str(e)}")
        except Timeout as e:
            self.logger.error(f"Request timed out: {str(e)}")
            raise APIError(f"API request timed out after {self.config.timeout} seconds")
        except RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            raise APIError(f"API request failed: {str(e)}")

    def query(self, query_text: str, conversation_context: List[Dict[str, str]]) -> Dict[str, Any]:
        self.logger.debug(f"Sending query with context length: {len(conversation_context)}")
        return self._make_request(
            'POST',
            '/api/query',
            json={
                'query': query_text,
                'conversation': conversation_context
            }
        )

    def health_check(self) -> Dict[str, Any]:
        return self._make_request('GET', '/api/health')


def create_app():
    app = Flask(__name__,
                static_url_path='/static',
                static_folder='static',
                template_folder='templates')

    session_manager = SessionManager(app)
    app.config['session_manager'] = session_manager

    asset_config = AssetConfig()
    app.config['asset_config'] = asset_config

    logger.info("Application initialized with SessionManager and AssetConfig")

    @app.context_processor
    def inject_asset_url():
        return {
            'asset_url': asset_config.asset_url,
            'get_asset_url': asset_config.get_asset_url
        }

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/chat', methods=['POST'])
    def chat():
        try:
            session_manager = app.config['session_manager']
            user_message = request.json.get('message', '')

            if not user_message:
                logger.warning(f"Empty message received (session: {session.get('session_id', 'unknown')[:8]}...)")
                return jsonify({"error": "Message is required"}), 400

            config = Config()
            context = session_manager.get_chat_context()
            client = APIClient(config)

            try:
                logger.info(
                    f"Processing chat request (session: {session['session_id'][:8]}..., context size: {len(context)})")
                response = client.query(user_message, context)
            except APIError as e:
                logger.error(f"API query failed (session: {session['session_id'][:8]}...): {str(e)}")
                return jsonify({
                    "error": "Failed to get response from API service",
                    "details": str(e)
                }), 503

            replies = response.get("result", {}).get("llm", {}).get("replies", ["No response received"])
            logger.info(f"Received {len(replies)} replies from API (session: {session['session_id'][:8]}...)")

            session_manager.update_chat_context("user", user_message, config.max_context_size)
            for reply in replies:
                session_manager.update_chat_context("Chipper", reply, config.max_context_size)

            return jsonify({
                "replies": replies,
                "timestamp": datetime.now().isoformat(),
                "session_id": session.get('session_id')
            })

        except Exception as e:
            session_id = session.get('session_id', 'unknown')
            logger.exception(f"Unexpected chat error (session: {session_id[:8]}...): {str(e)}")
            return jsonify({
                "error": "An unexpected error occurred",
                "details": str(e)
            }), 500

    @app.route('/api/clear', methods=['POST'])
    def clear_context():
        try:
            session_manager = app.config['session_manager']
            session_manager.clear_context()
            logger.info(f"Context cleared via API (session: {session.get('session_id', 'unknown')[:8]}...)")
            return jsonify({"status": "success"})
        except Exception as e:
            logger.error(f"Failed to clear context (session: {session.get('session_id', 'unknown')[:8]}...): {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/context-size', methods=['POST'])
    def update_context_size():
        try:
            new_size = int(request.json.get('size', 10))
            if new_size < 1:
                logger.warning(f"Invalid context size requested: {new_size}")
                return jsonify({"error": "Context size must be positive"}), 400

            session_manager = app.config['session_manager']
            context = session_manager.get_chat_context()
            if len(context) > new_size:
                context = context[-new_size:]
            session['context'] = context
            logger.info(f"Updated context size to: {new_size} (session: {session.get('session_id', 'unknown')[:8]}...)")
            return jsonify({"status": "success", "new_size": new_size})
        except ValueError as e:
            logger.error(f"Invalid context size value: {str(e)}")
            return jsonify({"error": "Invalid context size"}), 400

    @app.route('/api/assets/config', methods=['GET'])
    def get_asset_config():
        return jsonify({
            'assetUrl': asset_config.asset_url,
            'cacheTimeout': asset_config.cache_timeout,
            'debugMode': asset_config.debug_assets,
            'version': asset_config.asset_version
        })

    @app.route('/api/local-health', methods=['GET'])
    def local_health():
        try:
            config = Config()
            client = APIClient(config)
            api_health = client.health_check()

            return jsonify({
                "status": "healthy",
                "api_status": api_health,
                "config": {
                    "host": config.base_url,
                    "timeout": config.timeout,
                    "verify_ssl": config.verify_ssl,
                    "max_context_size": config.max_context_size,
                    "enable_caching": config.enable_caching,
                    "cache_timeout": config.cache_timeout
                },
                "asset_config": {
                    "asset_url": asset_config.asset_url,
                    "cache_timeout": asset_config.cache_timeout,
                    "debug_mode": asset_config.debug_assets,
                    "version": asset_config.asset_version
                }
            })
        except Exception as e:
            logger.exception("Health check failed")
            return jsonify({
                "status": "unhealthy",
                "error": str(e)
            }), 503

    @app.errorhandler(404)
    def not_found_error(error):
        logger.warning(f"404 error: {request.url}")
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 error: {str(error)}")
        return jsonify({"error": "Internal server error"}), 500

    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        uploads_dir = os.path.join(app.root_path, 'uploads')
        return send_from_directory(uploads_dir, filename)

    return app


if __name__ == '__main__':
    debug_mode = os.getenv('WEB_CLIENT_DEBUG', 'False').lower() == 'true'
    host = os.getenv('WEB_CLIENT_HOST', '0.0.0.0')
    port = int(os.getenv('WEB_CLIENT_PORT', '8321'))

    app = create_app()

    if debug_mode:
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

    logger.info(f"Starting web client application on {host}:{port} (debug={debug_mode})")
    app.run(host=host, port=port, debug=debug_mode)
