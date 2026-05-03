from __future__ import annotations

from app.config import AppSettings
from app.models.chat import ChatModel
from app.models.embeddings import EmbeddingModel
from app.models.providers.gemini import GeminiChatModel
from app.models.providers.groq import GroqChatModel
from app.models.providers.ollama import OllamaChatModel, OllamaEmbeddingModel


def build_chat_model(settings: AppSettings) -> ChatModel:
    provider = settings.chat.provider

    if provider == "ollama":
        return OllamaChatModel(settings.chat)
    if provider == "groq":
        return GroqChatModel(settings.chat)
    if provider == "gemini":
        return GeminiChatModel(settings.chat)

    raise ValueError(f"Unsupported chat provider: {provider}")


def build_embedding_model(settings: AppSettings) -> EmbeddingModel:
    provider = settings.embedding.provider

    if provider == "ollama":
        return OllamaEmbeddingModel(settings.embedding)

    raise ValueError(f"Unsupported embedding provider: {provider}")

