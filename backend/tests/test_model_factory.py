from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import load_settings
from app.models.factory import build_chat_model, build_embedding_model
from app.models.providers.gemini import GeminiChatModel
from app.models.providers.groq import GroqChatModel
from app.models.providers.ollama import OllamaChatModel, OllamaEmbeddingModel


class ModelFactoryTest(unittest.TestCase):
    def test_builds_default_ollama_models(self) -> None:
        settings = load_settings({})

        self.assertIsInstance(build_chat_model(settings), OllamaChatModel)
        self.assertIsInstance(build_embedding_model(settings), OllamaEmbeddingModel)

    def test_builds_groq_chat_model(self) -> None:
        settings = load_settings({"GHOST_RAILS_CHAT_PROVIDER": "groq", "GROQ_API_KEY": "secret"})

        self.assertIsInstance(build_chat_model(settings), GroqChatModel)

    def test_builds_gemini_chat_model(self) -> None:
        settings = load_settings({"GHOST_RAILS_CHAT_PROVIDER": "gemini", "GEMINI_API_KEY": "secret"})

        self.assertIsInstance(build_chat_model(settings), GeminiChatModel)

    def test_rejects_missing_cloud_api_key(self) -> None:
        settings = load_settings({"GHOST_RAILS_CHAT_PROVIDER": "groq"})

        with self.assertRaisesRegex(ValueError, "GROQ_API_KEY"):
            build_chat_model(settings)

    def test_rejects_unknown_embedding_provider(self) -> None:
        settings = load_settings({"GHOST_RAILS_EMBEDDING_PROVIDER": "unknown"})

        with self.assertRaisesRegex(ValueError, "Unsupported embedding provider"):
            build_embedding_model(settings)


if __name__ == "__main__":
    unittest.main()

