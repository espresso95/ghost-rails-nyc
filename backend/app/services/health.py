from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from app.config import AppSettings


@dataclass(frozen=True)
class HealthStatus:
    status: str
    environment: str
    model_profile: str
    ollama_available: bool
    vector_db_available: bool
    features_path: str
    sources_path: str
    chroma_path: str
    chat_provider: str
    chat_model: str
    embedding_provider: str
    embedding_model: str

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "environment": self.environment,
            "model_profile": self.model_profile,
            "ollama_available": self.ollama_available,
            "vector_db_available": self.vector_db_available,
            "features_path": self.features_path,
            "sources_path": self.sources_path,
            "chroma_path": self.chroma_path,
            "chat_provider": self.chat_provider,
            "chat_model": self.chat_model,
            "embedding_provider": self.embedding_provider,
            "embedding_model": self.embedding_model,
        }


def check_backend_health(settings: AppSettings) -> HealthStatus:
    vector_db_available = settings.chroma_path.exists()
    ollama_needed = settings.chat.provider == "ollama" or settings.embedding.provider == "ollama"
    ollama_available = check_ollama(settings.chat.base_url if settings.chat.provider == "ollama" else settings.embedding.base_url)

    status = "ok"
    if ollama_needed and not ollama_available:
        status = "degraded"

    return HealthStatus(
        status=status,
        environment=settings.env,
        model_profile=settings.model_profile,
        ollama_available=ollama_available,
        vector_db_available=vector_db_available,
        features_path=str(settings.features_path),
        sources_path=str(settings.sources_path),
        chroma_path=str(settings.chroma_path),
        chat_provider=settings.chat.provider,
        chat_model=settings.chat.model,
        embedding_provider=settings.embedding.provider,
        embedding_model=settings.embedding.model,
    )


def check_ollama(base_url: str, timeout_seconds: float = 0.5) -> bool:
    url = f"{base_url.rstrip('/')}/api/tags"
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            body = response.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError, OSError):
        return False

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return False

    return isinstance(payload, dict)

