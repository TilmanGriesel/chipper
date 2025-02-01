import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, Optional

from api.config import SYSTEM_PROMPT_VALUE, logger
from core.pipeline_config import ModelProvider, QueryPipelineConfig


class EnvKeys(str, Enum):
    PROVIDER = "PROVIDER"
    MODEL_NAME = "MODEL_NAME"
    HF_MODEL_NAME = "HF_MODEL_NAME"
    EMBEDDING_MODEL = "EMBEDDING_MODEL_NAME"
    HF_EMBEDDING_MODEL = "HF_EMBEDDING_MODEL_NAME"
    HF_API_KEY = "HF_API_KEY"
    OLLAMA_URL = "OLLAMA_URL"
    ALLOW_MODEL_PULL = "ALLOW_MODEL_PULL"
    ES_URL = "ES_URL"
    ES_INDEX = "ES_INDEX"
    ES_TOP_K = "ES_TOP_K"
    ES_NUM_CANDIDATES = "ES_NUM_CANDIDATES"
    ES_BASIC_AUTH_USER = "ES_BASIC_AUTH_USERNAME"
    ES_BASIC_AUTH_PASSWORD = "ES_BASIC_AUTH_PASSWORD"
    ENABLE_CONVERSATION_LOGS = "ENABLE_CONVERSATION_LOGS"


@dataclass
class GenerationParams:
    context_window: tuple[str, type, str] = ("CONTEXT_WINDOW", int, "8192")
    temperature: tuple[str, type, None] = ("TEMPERATURE", float, None)
    seed: tuple[str, type, None] = ("SEED", int, None)
    top_k: tuple[str, type, None] = ("TOP_K", int, None)
    top_p: tuple[str, type, None] = ("TOP_P", float, None)
    min_p: tuple[str, type, None] = ("MIN_P", float, None)
    repeat_last_n: tuple[str, type, None] = ("REPEAT_LAST_N", int, None)
    repeat_penalty: tuple[str, type, None] = ("REPEAT_PENALTY", float, None)
    num_predict: tuple[str, type, None] = ("NUM_PREDICT", int, None)
    tfs_z: tuple[str, type, None] = ("TFS_Z", float, None)


def get_env_value(
    key: str, converter: Optional[Callable] = None, default: Optional[str] = None
) -> Any:
    """Get and convert environment variable value with optional default."""
    value = os.getenv(key)
    if value is None:
        return None

    if converter:
        try:
            return converter(default if value == "" else value)
        except (ValueError, TypeError):
            return None
    return value


def get_provider_specific_config() -> dict[str, Any]:
    """Get provider-specific configuration."""
    provider = (
        ModelProvider.HUGGINGFACE
        if os.getenv(EnvKeys.PROVIDER, "ollama").lower() == "hf"
        else ModelProvider.OLLAMA
    )

    config = {
        "provider": provider,
        "model_name": os.getenv(
            EnvKeys.HF_MODEL_NAME
            if provider == ModelProvider.HUGGINGFACE
            else EnvKeys.MODEL_NAME
        ),
        "embedding_model": os.getenv(
            EnvKeys.HF_EMBEDDING_MODEL
            if provider == ModelProvider.HUGGINGFACE
            else EnvKeys.EMBEDDING_MODEL
        ),
        "system_prompt": SYSTEM_PROMPT_VALUE,
    }

    if provider == ModelProvider.HUGGINGFACE:
        config["hf_api_key"] = os.getenv(EnvKeys.HF_API_KEY)
    elif ollama_url := os.getenv(EnvKeys.OLLAMA_URL):
        config["ollama_url"] = ollama_url

    return config


def get_elasticsearch_config(index: Optional[str] = None) -> dict[str, Any]:
    """Get Elasticsearch configuration if enabled."""
    if not (es_url := os.getenv(EnvKeys.ES_URL)):
        return {}

    config = {
        "es_url": es_url,
        "es_index": index or os.getenv(EnvKeys.ES_INDEX),
        "es_basic_auth_user": os.getenv(EnvKeys.ES_BASIC_AUTH_USER),
        "es_basic_auth_password": os.getenv(EnvKeys.ES_BASIC_AUTH_PASSWORD),
    }

    for env_key, default in [
        (EnvKeys.ES_TOP_K, "5"),
        (EnvKeys.ES_NUM_CANDIDATES, "-1"),
    ]:
        if value := get_env_value(env_key, int, default):
            config[env_key.lower()] = value

    return config


def create_pipeline_config(
    model: Optional[str] = None,
    index: Optional[str] = None,
    temperature: Optional[float] = None,
    top_k: Optional[int] = None,
    top_p: Optional[float] = None,
    min_p: Optional[float] = None,
    repeat_last_n: Optional[int] = None,
    repeat_penalty: Optional[float] = None,
    num_predict: Optional[int] = None,
    tfs_z: Optional[float] = None,
    context_window: Optional[int] = None,
    seed: Optional[int] = None,
    **additional_params: Dict[str, Any],
) -> QueryPipelineConfig:
    """Create pipeline configuration from environment variables with optional parameter overrides."""
    config = get_provider_specific_config()
    if model:
        config["model_name"] = model

    # Add generation parameters from environment first
    params = GenerationParams()
    for param in params.__annotations__:
        env_key, converter, default = getattr(params, param)
        if value := get_env_value(env_key, converter, default):
            config[param] = value

    # Override with any provided parameters
    generation_params = {
        "temperature": temperature,
        "top_k": top_k,
        "top_p": top_p,
        "min_p": min_p,
        "repeat_last_n": repeat_last_n,
        "repeat_penalty": repeat_penalty,
        "num_predict": num_predict,
        "tfs_z": tfs_z,
        "context_window": context_window,
        "seed": seed,
    }

    # Update config with provided non-None parameters
    config.update({k: v for k, v in generation_params.items() if v is not None})

    # Add any additional parameters passed
    config.update(additional_params)

    # Add mirostat parameters
    if mirostat := get_env_value("MIROSTAT", int):
        config["mirostat"] = mirostat
        for param in ["MIROSTAT_ETA", "MIROSTAT_TAU"]:
            if value := get_env_value(param, float):
                config[param.lower()] = value

    # Add model pull configuration
    if allow_pull := os.getenv(EnvKeys.ALLOW_MODEL_PULL):
        config["allow_model_pull"] = allow_pull.lower() == "true"

    # Add conversation logs setting
    if value := os.getenv(EnvKeys.ENABLE_CONVERSATION_LOGS):
        config["enable_conversation_logs"] = value.lower() == "true"

    # Add stop sequence
    if stop_sequence := os.getenv("STOP_SEQUENCE"):
        config["stop_sequence"] = stop_sequence

    # Add Elasticsearch config
    config.update(get_elasticsearch_config(index))

    logger.info("\nPipeline Configuration:")
    for key, value in sorted(config.items()):
        if any(sensitive in key.lower() for sensitive in ["password", "key", "auth"]):
            logger.info(f"  {key}: ****")
        else:
            logger.info(f"  {key}: {value}")

    return QueryPipelineConfig(**config)
