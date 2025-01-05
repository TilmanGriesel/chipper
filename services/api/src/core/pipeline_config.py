from dataclasses import dataclass


@dataclass
class PipelineConfig:
    es_url: str
    es_index: str
    ollama_url: str
    embedding_model: str
    allow_model_pull: bool


@dataclass
class QueryPipelineConfig(PipelineConfig):
    model_name: str
    system_prompt: str
    context_window: int
    temperature: float
    seed: int
    top_k: int
