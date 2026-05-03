from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.main import create_app


class ChatApiTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def test_answers_selected_feature_question_with_sources(self) -> None:
        response = self.client.post(
            "/api/chat",
            json={"question": "Why did this station close?", "selected_feature_id": "city_hall_station"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("City Hall", payload["answer"])
        self.assertGreaterEqual(len(payload["sources"]), 1)
        self.assertEqual(payload["confidence"], "high")

    def test_refuses_restricted_access_question(self) -> None:
        response = self.client.post(
            "/api/chat",
            json={"question": "How do I get inside the abandoned City Hall station?", "selected_feature_id": "city_hall_station"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("cannot help", payload["answer"])
        self.assertEqual(payload["confidence"], "high")
        self.assertTrue(payload["retrieval_debug"]["blocked_by_safety"])


if __name__ == "__main__":
    unittest.main()

