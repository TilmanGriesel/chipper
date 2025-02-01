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

    if env_prompt is not None and env_prompt.strip() is not "":
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

def log_environment_variables():
    logger.info("================== Environment Variables ==================")

    # Version Info
    logger.info("Version Info:")
    logger.info(f"  APP_VERSION: {os.getenv('APP_VERSION', 'Not set')}")
    logger.info(f"  APP_BUILD_NUM: {os.getenv('APP_BUILD_NUM', 'Not set')}")

    # Provider Configuration
    logger.info("Provider Configuration:")
    logger.info(f"  PROVIDER: {os.getenv('PROVIDER', 'Not set')}")
    logger.info(f"  OLLAMA_URL: {os.getenv('OLLAMA_URL', 'Not set')}")

    # Permission Settings
    logger.info("Permission Settings:")
    logger.info(f"  ALLOW_MODEL_PULL: {os.getenv('ALLOW_MODEL_PULL', 'Not set')}")
    logger.info(f"  ALLOW_MODEL_CHANGE: {os.getenv('ALLOW_MODEL_CHANGE', 'Not set')}")
    logger.info(f"  ALLOW_INDEX_CHANGE: {os.getenv('ALLOW_INDEX_CHANGE', 'Not set')}")
    logger.info(f"  IGNORE_MODEL_REQUEST: {os.getenv('IGNORE_MODEL_REQUEST', 'Not set')}")

    # Model Configuration
    logger.info("Model Configuration:")
    logger.info(f"  EMBEDDING_MODEL_NAME: {os.getenv('EMBEDDING_MODEL_NAME', 'Not set')}")
    logger.info(f"  HF_EMBEDDING_MODEL_NAME: {os.getenv('HF_EMBEDDING_MODEL_NAME', 'Not set')}")
    logger.info(f"  MODEL_NAME: {os.getenv('MODEL_NAME', 'Not set')}")
    logger.info(f"  HF_MODEL_NAME: {os.getenv('HF_MODEL_NAME', 'Not set')}")
    logger.info(f"  CONTEXT_WINDOW: {os.getenv('CONTEXT_WINDOW', 'Not set')}")

    # Elasticsearch Configuration
    logger.info("Elasticsearch Configuration:")
    logger.info(f"  ES_URL: {os.getenv('ES_URL', 'Not set')}")
    logger.info(f"  ES_INDEX: {os.getenv('ES_INDEX', 'Not set')}")
    logger.info(f"  ES_TOP_K: {os.getenv('ES_TOP_K', 'Not set')}")
    logger.info(f"  ES_NUM_CANDIDATES: {os.getenv('ES_NUM_CANDIDATES', 'Not set')}")

    # API Settings (excluding sensitive data)
    logger.info("API Configuration:")
    logger.info(f"  HOST: {os.getenv('HOST', 'Not set')}")
    logger.info(f"  PORT: {os.getenv('PORT', 'Not set')}")
    logger.info(f"  REQUIRE_API_KEY: {os.getenv('REQUIRE_API_KEY', 'Not set')}")
    logger.info(f"  MINUTE_RATE_LIMIT: {os.getenv('MINUTE_RATE_LIMIT', 'Not set')}")
    logger.info(f"  DAILY_RATE_LIMIT: {os.getenv('DAILY_RATE_LIMIT', 'Not set')}")
    logger.info(f"  REQUIRE_SECURE: {os.getenv('REQUIRE_SECURE', 'Not set')}")
    logger.info(f"  DEBUG: {os.getenv('DEBUG', 'Not set')}")

    # System Settings
    logger.info("System Configuration:")
    logger.info(f"  SYSTEM_PROMPT_PATH: {os.getenv('SYSTEM_PROMPT_PATH', 'Not set')}")
    logger.info(f"  SYSTEM_PROMPT: {os.getenv('SYSTEM_PROMPT', 'Not set')}")
    logger.info(f"  ENABLE_CONVERSATION_LOGS: {os.getenv('ENABLE_CONVERSATION_LOGS', 'Not set')}")

    # Model Generation Parameters
    logger.info("Model Generation Parameters:")
    logger.info(f"  TEMPERATURE: {os.getenv('TEMPERATURE', 'Not set')}")
    logger.info(f"  SEED: {os.getenv('SEED', 'Not set')}")
    logger.info(f"  TOP_K: {os.getenv('TOP_K', 'Not set')}")
    logger.info(f"  TOP_P: {os.getenv('TOP_P', 'Not set')}")
    logger.info(f"  MIN_P: {os.getenv('MIN_P', 'Not set')}")
    logger.info(f"  MIROSTAT: {os.getenv('MIROSTAT', 'Not set')}")
    logger.info(f"  MIROSTAT_ETA: {os.getenv('MIROSTAT_ETA', 'Not set')}")
    logger.info(f"  MIROSTAT_TAU: {os.getenv('MIROSTAT_TAU', 'Not set')}")
    logger.info(f"  REPEAT_LAST_N: {os.getenv('REPEAT_LAST_N', 'Not set')}")
    logger.info(f"  REPEAT_PENALTY: {os.getenv('REPEAT_PENALTY', 'Not set')}")
    logger.info(f"  NUM_PREDICT: {os.getenv('NUM_PREDICT', 'Not set')}")
    logger.info(f"  TFS_Z: {os.getenv('TFS_Z', 'Not set')}")

    logger.info("=====================================================")


log_environment_variables()
