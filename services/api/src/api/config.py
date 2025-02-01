import logging
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App configuration
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

# Version information
APP_VERSION = os.getenv("APP_VERSION", "[DEV]")
BUILD_NUMBER = os.getenv("APP_BUILD_NUM", "0")

# Provider settings
PROVIDER_IS_OLLAMA = os.getenv("PROVIDER", "ollama") == "ollama"

# Feature flags
ALLOW_MODEL_CHANGE = os.getenv("ALLOW_MODEL_CHANGE", "true").lower() == "true"
ALLOW_INDEX_CHANGE = os.getenv("ALLOW_INDEX_CHANGE", "true").lower() == "true"
ALLOW_MODEL_PARAMETER_CHANGE = (
    os.getenv("ALLOW_MODEL_PARAMETER_CHANGE", "true").lower() == "true"
)
IGNORE_MODEL_REQUEST = os.getenv("IGNORE_MODEL_REQUEST", "true").lower() == "true"
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# Rate limiting configuration
DAILY_LIMIT = int(os.getenv("DAILY_RATE_LIMIT", "86400"))
MINUTE_LIMIT = int(os.getenv("MINUTE_RATE_LIMIT", "60"))
STORAGE_URI = os.getenv("RATE_LIMIT_STORAGE", "memory://")

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[f"{DAILY_LIMIT} per day", f"{MINUTE_LIMIT} per minute"],
    storage_uri=STORAGE_URI,
)

# API Key configuration
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    API_KEY = secrets.token_urlsafe(32)
    logger.info(f"Generated API key: {API_KEY}")


def load_systemprompt(base_path: str) -> str:
    default_prompt = ""
    env_var_name = "SYSTEM_PROMPT"
    env_prompt = os.getenv(env_var_name)

    if env_prompt is not None and env_prompt.strip() != "":
        content = env_prompt.strip()
        logger.info(
            f"Using system prompt from '{env_var_name}' environment variable; content: '{content}'"
        )
        return content

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


SYSTEM_PROMPT_VALUE = load_systemprompt(os.getenv("SYSTEM_PROMPT_PATH", os.getcwd()))
