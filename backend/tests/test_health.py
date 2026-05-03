from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.config import load_settings
from app.main import create_app
from app.services.health import check_backend_health


class HealthServiceTest(unittest.TestCase):
    def test_reports_degraded_when_ollama_is_required_but_unavailable(self) -> None:
        settings = load_settings({})

        with patch("app.services.health.check_ollama", return_value=False):
            health = check_backend_health(settings)

        self.assertEqual(health.status, "degraded")
        self.assertFalse(health.ollama_available)
        self.assertEqual(health.chat_provider, "ollama")

    def test_reports_ok_when_cloud_chat_uses_local_embedding_and_ollama_is_available(self) -> None:
        settings = load_settings(
            {
                "GHOST_RAILS_CHAT_PROVIDER": "groq",
                "GROQ_API_KEY": "secret",
                "GHOST_RAILS_EMBEDDING_PROVIDER": "ollama",
            }
        )

        with patch("app.services.health.check_ollama", return_value=True):
            health = check_backend_health(settings)

        self.assertEqual(health.status, "ok")
        self.assertTrue(health.ollama_available)
        self.assertEqual(health.chat_provider, "groq")


class HealthApiTest(unittest.TestCase):
    def test_health_endpoint_returns_status_payload(self) -> None:
        app = create_app()

        with patch("app.services.health.check_ollama", return_value=False):
            response = TestClient(app).get("/api/health")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "degraded")
        self.assertEqual(payload["model_profile"], "local_m2_16gb")
        self.assertIn("vector_db_available", payload)


if __name__ == "__main__":
    unittest.main()

