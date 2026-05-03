from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.main import create_app


class StationsApiTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def test_lists_stations_by_route(self) -> None:
        response = self.client.get("/api/stations", params={"route": "6"})

        self.assertEqual(response.status_code, 200)
        stations = response.json()["stations"]
        self.assertGreaterEqual(len(stations), 1)
        self.assertTrue(any(station["name"] == "Brooklyn Bridge-City Hall" for station in stations))

    def test_nearby_stations(self) -> None:
        response = self.client.get("/api/stations/nearby", params={"lat": 40.7131, "lon": -74.0048, "radius_m": 300})

        self.assertEqual(response.status_code, 200)
        station_names = [result["station"]["name"] for result in response.json()["results"]]
        self.assertIn("Brooklyn Bridge-City Hall", station_names)


if __name__ == "__main__":
    unittest.main()

