from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import DEFAULT_GROQ_BASE_URL, DEFAULT_OLLAMA_BASE_URL, load_settings


REPO_ROOT = Path(__file__).resolve().parents[2]


class LoadSettingsTest(unittest.TestCase):
    def test_defaults_use_low_ram_local_profile(self) -> None:
        settings = load_settings({})

        self.assertEqual(settings.model_profile, "local_m2_16gb")
        self.assertEqual(settings.chat.provider, "ollama")
        self.assertEqual(settings.chat.model, "llama3.2:3b")
        self.assertEqual(settings.chat.base_url, DEFAULT_OLLAMA_BASE_URL)
        self.assertEqual(settings.embedding.provider, "ollama")
        self.assertEqual(settings.embedding.model, "nomic-embed-text")
        self.assertEqual(settings.retrieval.similarity_top_k, 6)
        self.assertEqual(settings.retrieval.context_chunks, 3)
        self.assertEqual(settings.retrieval.max_context_tokens, 3500)

    def test_chat_and_embedding_roles_are_configured_independently(self) -> None:
        settings = load_settings(
            {
                "GHOST_RAILS_CHAT_PROVIDER": "groq",
                "GHOST_RAILS_CHAT_MODEL": "llama-3.3-70b-versatile",
                "GROQ_API_KEY": "secret",
                "GHOST_RAILS_EMBEDDING_PROVIDER": "ollama",
                "GHOST_RAILS_EMBEDDING_MODEL": "mxbai-embed-large",
                "OLLAMA_BASE_URL": "http://localhost:11435",
            }
        )

        self.assertEqual(settings.chat.provider, "groq")
        self.assertEqual(settings.chat.model, "llama-3.3-70b-versatile")
        self.assertEqual(settings.chat.base_url, DEFAULT_GROQ_BASE_URL)
        self.assertEqual(settings.chat.api_key, "secret")
        self.assertEqual(settings.embedding.provider, "ollama")
        self.assertEqual(settings.embedding.model, "mxbai-embed-large")
        self.assertEqual(settings.embedding.base_url, "http://localhost:11435")

    def test_embedding_index_path_includes_embedding_profile(self) -> None:
        settings = load_settings(
            {
                "GHOST_RAILS_CHROMA_PATH": "data/chroma",
                "GHOST_RAILS_EMBEDDING_PROVIDER": "ollama",
                "GHOST_RAILS_EMBEDDING_MODEL": "nomic-embed-text",
            }
        )

        self.assertEqual(settings.embedding_index_path, REPO_ROOT / "data/chroma/ollama-nomic-embed-text")

    def test_invalid_integer_setting_raises_clear_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "GHOST_RAILS_API_PORT must be an integer"):
            load_settings({"GHOST_RAILS_API_PORT": "not-a-port"})


if __name__ == "__main__":
    unittest.main()
