from __future__ import annotations

from typing import Sequence

from app.config import ChatModelSettings, EmbeddingModelSettings
from app.models.chat import ChatMessage, ChatOptions, ChatResponse
from app.models.embeddings import EmbeddingResponse
from app.models.errors import ModelProviderError
from app.models.providers.http import post_json


class OllamaChatModel:
    provider = "ollama"

    def __init__(self, settings: ChatModelSettings) -> None:
        self.settings = settings
        self.model = settings.model
        self.base_url = settings.base_url.rstrip("/")

    def complete(self, messages: Sequence[ChatMessage], options: ChatOptions | None = None) -> ChatResponse:
        options = options or ChatOptions()
        payload = {
            "model": self.model,
            "messages": [message.as_dict() for message in messages],
            "stream": False,
            "options": {
                "temperature": self.settings.temperature if options.temperature is None else options.temperature,
                "num_predict": self.settings.max_output_tokens
                if options.max_output_tokens is None
                else options.max_output_tokens,
            },
        }
        response = post_json(
            f"{self.base_url}/api/chat",
            payload,
            timeout_seconds=self.settings.timeout_seconds,
            label="Ollama chat",
        )
        message = response.get("message")
        if not isinstance(message, dict) or not isinstance(message.get("content"), str):
            raise ModelProviderError("Ollama chat returned no message content")
        return ChatResponse(text=message["content"], provider=self.provider, model=self.model, raw=response)


class OllamaEmbeddingModel:
    provider = "ollama"

    def __init__(self, settings: EmbeddingModelSettings) -> None:
        self.settings = settings
        self.model = settings.model
        self.base_url = settings.base_url.rstrip("/")

    def embed(self, texts: Sequence[str]) -> EmbeddingResponse:
        payload = {"model": self.model, "input": list(texts)}
        response = post_json(
            f"{self.base_url}/api/embed",
            payload,
            timeout_seconds=self.settings.timeout_seconds,
            label="Ollama embeddings",
        )
        embeddings = response.get("embeddings")
        if not _is_embedding_batch(embeddings):
            raise ModelProviderError("Ollama embeddings returned no embedding batch")
        return EmbeddingResponse(
            embeddings=[list(vector) for vector in embeddings],
            provider=self.provider,
            model=self.model,
            raw=response,
        )


def _is_embedding_batch(value: object) -> bool:
    if not isinstance(value, list):
        return False
    return all(_is_embedding_vector(item) for item in value)


def _is_embedding_vector(value: object) -> bool:
    if not isinstance(value, list):
        return False
    return all(isinstance(item, int | float) for item in value)

