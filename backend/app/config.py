from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ChatModelSettings:
    provider: str
    model: str
    base_url: str
    timeout_seconds: int
    temperature: float
    max_output_tokens: int
    api_key: str | None = None


@dataclass(frozen=True)
class EmbeddingModelSettings:
    provider: str
    model: str
    base_url: str
    timeout_seconds: int
    api_key: str | None = None


@dataclass(frozen=True)
class RetrievalSettings:
    similarity_top_k: int
    context_chunks: int
    max_context_tokens: int


@dataclass(frozen=True)
class AppSettings:
    env: str
    api_host: str
    api_port: int
    model_profile: str
    features_path: Path
    sources_path: Path
    chroma_path: Path
    chat: ChatModelSettings
    embedding: EmbeddingModelSettings
    retrieval: RetrievalSettings
    enable_llm_answers: bool

    @property
    def embedding_index_path(self) -> Path:
        return self.chroma_path / f"{_slug(self.embedding.provider)}-{_slug(self.embedding.model)}"


def load_settings(env: Mapping[str, str] | None = None) -> AppSettings:
    values = os.environ if env is None else env
    ollama_base_url = _read(values, "OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL)

    chat_provider = _read(values, "GHOST_RAILS_CHAT_PROVIDER", "ollama").lower()
    embedding_provider = _read(values, "GHOST_RAILS_EMBEDDING_PROVIDER", "ollama").lower()

    chat = ChatModelSettings(
        provider=chat_provider,
        model=_read(values, "GHOST_RAILS_CHAT_MODEL", _default_chat_model(chat_provider)),
        base_url=_read(values, "GHOST_RAILS_CHAT_BASE_URL", _default_chat_base_url(chat_provider, ollama_base_url)),
        timeout_seconds=_read_int(values, "GHOST_RAILS_CHAT_TIMEOUT_SECONDS", 120),
        temperature=_read_float(values, "GHOST_RAILS_CHAT_TEMPERATURE", 0.1),
        max_output_tokens=_read_int(values, "GHOST_RAILS_CHAT_MAX_OUTPUT_TOKENS", 512),
        api_key=_provider_api_key(values, "CHAT", chat_provider),
    )

    embedding = EmbeddingModelSettings(
        provider=embedding_provider,
        model=_read(values, "GHOST_RAILS_EMBEDDING_MODEL", _default_embedding_model(embedding_provider)),
        base_url=_read(
            values,
            "GHOST_RAILS_EMBEDDING_BASE_URL",
            _default_embedding_base_url(embedding_provider, ollama_base_url),
        ),
        timeout_seconds=_read_int(values, "GHOST_RAILS_EMBEDDING_TIMEOUT_SECONDS", 120),
        api_key=_provider_api_key(values, "EMBEDDING", embedding_provider),
    )

    retrieval = RetrievalSettings(
        similarity_top_k=_read_int(values, "GHOST_RAILS_SIMILARITY_TOP_K", 6),
        context_chunks=_read_int(values, "GHOST_RAILS_CONTEXT_CHUNKS", 3),
        max_context_tokens=_read_int(values, "GHOST_RAILS_MAX_CONTEXT_TOKENS", 3500),
    )

    return AppSettings(
        env=_read(values, "GHOST_RAILS_ENV", "development"),
        api_host=_read(values, "GHOST_RAILS_API_HOST", "127.0.0.1"),
        api_port=_read_int(values, "GHOST_RAILS_API_PORT", 8000),
        model_profile=_read(values, "GHOST_RAILS_MODEL_PROFILE", "local_m2_16gb"),
        features_path=_resolve_repo_path(_read(values, "GHOST_RAILS_FEATURES_PATH", "data/features/features.geojson")),
        sources_path=_resolve_repo_path(_read(values, "GHOST_RAILS_SOURCES_PATH", "data/sources")),
        chroma_path=_resolve_repo_path(_read(values, "GHOST_RAILS_CHROMA_PATH", "data/chroma")),
        chat=chat,
        embedding=embedding,
        retrieval=retrieval,
        enable_llm_answers=_read_bool(values, "GHOST_RAILS_ENABLE_LLM_ANSWERS", False),
    )


def _default_chat_model(provider: str) -> str:
    defaults = {
        "ollama": "llama3.2:3b",
        "groq": "llama-3.1-8b-instant",
        "gemini": "gemini-2.5-flash-lite",
    }
    return defaults.get(provider, "")


def _default_embedding_model(provider: str) -> str:
    defaults = {
        "ollama": "nomic-embed-text",
    }
    return defaults.get(provider, "")


def _default_chat_base_url(provider: str, ollama_base_url: str) -> str:
    defaults = {
        "ollama": ollama_base_url,
        "groq": DEFAULT_GROQ_BASE_URL,
        "gemini": DEFAULT_GEMINI_BASE_URL,
    }
    return defaults.get(provider, "")


def _default_embedding_base_url(provider: str, ollama_base_url: str) -> str:
    defaults = {
        "ollama": ollama_base_url,
    }
    return defaults.get(provider, "")


def _provider_api_key(values: Mapping[str, str], role: str, provider: str) -> str | None:
    key_names = [
        f"GHOST_RAILS_{role}_API_KEY",
        f"GHOST_RAILS_{provider.upper()}_API_KEY",
        f"{provider.upper()}_API_KEY",
    ]
    for key_name in key_names:
        value = values.get(key_name)
        if value:
            return value
    return None


def _read(values: Mapping[str, str], name: str, default: str) -> str:
    value = values.get(name)
    return default if value is None or value == "" else value


def _read_int(values: Mapping[str, str], name: str, default: int) -> int:
    value = values.get(name)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError as error:
        raise ValueError(f"{name} must be an integer") from error


def _read_float(values: Mapping[str, str], name: str, default: float) -> float:
    value = values.get(name)
    if value is None or value == "":
        return default
    try:
        return float(value)
    except ValueError as error:
        raise ValueError(f"{name} must be a number") from error


def _read_bool(values: Mapping[str, str], name: str, default: bool) -> bool:
    value = values.get(name)
    if value is None or value == "":
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be a boolean")


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "default"


def _resolve_repo_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return REPO_ROOT / path
