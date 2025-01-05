from dataclasses import dataclass, field
from typing import Optional


class ModelProvider:
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"


def _default_none() -> None:
    return None


@dataclass
class QueryPipelineConfig:
    """Base configuration for all pipelines."""

    # Required parameters
    es_url: str
    es_index: str
    ollama_url: str
    embedding_model: str
    model_name: str
    system_prompt: str
    context_window: int
    temperature: float
    seed: int
    top_k: int

    # Optional parameters with field defaults
    provider: str = field(default=ModelProvider.OLLAMA)
    hf_api_key: Optional[str] = field(default_factory=_default_none)
    allow_model_pull: bool = field(default=True)

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.provider == ModelProvider.HUGGINGFACE and not self.hf_api_key:
            raise ValueError(
                "HuggingFace API key is required when using HuggingFace provider"
            )

        if self.provider not in [ModelProvider.OLLAMA, ModelProvider.HUGGINGFACE]:
            raise ValueError(f"Unsupported provider: {self.provider}")
