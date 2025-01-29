import os

from api.config import system_prompt_value
from core.pipeline_config import ModelProvider, QueryPipelineConfig


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
        for param in ["MIROSTAT_ETA", "MIROSTAT_TAU"]:
            if (value := get_env_param(param, float)) is not None:
                config_params[param.lower()] = value

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

    if (enable_conversation_logs := os.getenv("ENABLE_CONVERSATION_LOGS")) is not None:
        config_params["enable_conversation_logs"] = enable_conversation_logs

    return QueryPipelineConfig(**config_params)
