from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.main import create_app


class FeatureApiTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def test_lists_features(self) -> None:
        response = self.client.get("/api/features")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["type"], "FeatureCollection")
        self.assertGreaterEqual(len(payload["features"]), 20)

    def test_filters_features_by_borough_and_type(self) -> None:
        response = self.client.get("/api/features", params={"borough": "Queens", "feature_type": "disused_corridor"})

        self.assertEqual(response.status_code, 200)
        features = response.json()["features"]
        self.assertGreaterEqual(len(features), 1)
        self.assertTrue(all(feature["properties"]["borough"] == "Queens" for feature in features))
        self.assertTrue(all(feature["properties"]["feature_type"] == "disused_corridor" for feature in features))

    def test_gets_feature_detail(self) -> None:
        response = self.client.get("/api/features/city_hall_station")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["properties"]["name"], "City Hall Station")

    def test_search_finds_city_hall(self) -> None:
        response = self.client.get("/api/search", params={"q": "City Hall"})

        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]["feature"]["properties"]["id"], "city_hall_station")

    def test_nearby_finds_city_hall(self) -> None:
        response = self.client.get("/api/features/nearby", params={"lat": 40.7134, "lon": -74.0049, "radius_m": 500})

        self.assertEqual(response.status_code, 200)
        ids = [result["feature"]["properties"]["id"] for result in response.json()["results"]]
        self.assertIn("city_hall_station", ids)


if __name__ == "__main__":
    unittest.main()

