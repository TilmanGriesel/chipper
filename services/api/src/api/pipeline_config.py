import os
from enum import Enum
from typing import Any, Optional, TypeVar, Callable

from api.config import system_prompt_value
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
    FILTER_THINK_TAG_CONTENT = "FILTER_THINK_TAG_CONTENT"


T = TypeVar('T')

def get_env_param(param_name: str, converter: Optional[Callable[[str], T]] = None, default: Optional[str] = None) -> Optional[T]:
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


def create_pipeline_config(model: Optional[str] = None, index: Optional[str] = None) -> QueryPipelineConfig:
    # Determine provider
    provider = (
        ModelProvider.HUGGINGFACE
        if os.getenv(EnvKeys.PROVIDER, "ollama").lower() == "hf"
        else ModelProvider.OLLAMA
    )

    # Get model names based on provider
    model_name = model or os.getenv(
        EnvKeys.HF_MODEL_NAME if provider == ModelProvider.HUGGINGFACE else EnvKeys.MODEL_NAME
    )
    embedding_model = os.getenv(
        EnvKeys.HF_EMBEDDING_MODEL if provider == ModelProvider.HUGGINGFACE else EnvKeys.EMBEDDING_MODEL
    )

    # Initialize base configuration
    config: dict[str, Any] = {
        "provider": provider,
        "model_name": model_name,
        "embedding_model": embedding_model,
        "system_prompt": system_prompt_value,
    }

    # Provider-specific authentication
    if provider == ModelProvider.HUGGINGFACE:
        config["hf_api_key"] = os.getenv(EnvKeys.HF_API_KEY)
    elif (ollama_url := os.getenv(EnvKeys.OLLAMA_URL)):
        config["ollama_url"] = ollama_url

    # Model pull configuration
    if (allow_pull := os.getenv(EnvKeys.ALLOW_MODEL_PULL)):
        config["allow_model_pull"] = allow_pull.lower() == "true"

    # Generation parameters with types
    generation_params = {
        "CONTEXT_WINDOW": ("context_window", int, "8192"),
        "TEMPERATURE": ("temperature", float, None),
        "SEED": ("seed", int, None),
        "TOP_K": ("top_k", int, None),
        "TOP_P": ("top_p", float, None),
        "MIN_P": ("min_p", float, None),
        "REPEAT_LAST_N": ("repeat_last_n", int, None),
        "REPEAT_PENALTY": ("repeat_penalty", float, None),
        "NUM_PREDICT": ("num_predict", int, None),
        "TFS_Z": ("tfs_z", float, None)
    }

    for env_key, (config_key, param_type, default) in generation_params.items():
        if (value := get_env_param(env_key, param_type, default)) is not None:
            config[config_key] = value

    # Mirostat parameters
    if (mirostat := get_env_param("MIROSTAT", int)) is not None:
        config["mirostat"] = mirostat
        for param in ["MIROSTAT_ETA", "MIROSTAT_TAU"]:
            if (value := get_env_param(param, float)) is not None:
                config[param.lower()] = value

    # Elasticsearch configuration
    if (es_url := os.getenv(EnvKeys.ES_URL)):
        config.update({
            "es_url": es_url,
            "es_index": index or os.getenv(EnvKeys.ES_INDEX),
            "es_basic_auth_user": os.getenv(EnvKeys.ES_BASIC_AUTH_USER),
            "es_basic_auth_password": os.getenv(EnvKeys.ES_BASIC_AUTH_PASSWORD)
        })

        es_params = {
            EnvKeys.ES_TOP_K: ("es_top_k", "5"),
            EnvKeys.ES_NUM_CANDIDATES: ("es_num_candidates", "-1")
        }
        for env_key, (config_key, default) in es_params.items():
            if (value := get_env_param(env_key, int, default)) is not None:
                config[config_key] = value

    # Boolean settings
    bool_settings = {
        EnvKeys.ENABLE_CONVERSATION_LOGS: "enable_conversation_logs",
    }
    for env_key, config_key in bool_settings.items():
        if (value := os.getenv(env_key)) is not None:
            config[config_key] = value.lower() == "true"

    # Stop sequence
    if (stop_sequence := os.getenv("STOP_SEQUENCE")):
        config["stop_sequence"] = stop_sequence

    return QueryPipelineConfig(**config)
