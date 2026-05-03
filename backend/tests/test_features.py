from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.geo.features import get_feature_by_id, load_feature_collection


REPO_ROOT = Path(__file__).resolve().parents[2]
FEATURES_PATH = REPO_ROOT / "data" / "features" / "features.geojson"


class FeatureDatasetTest(unittest.TestCase):
    def test_loads_curated_feature_collection(self) -> None:
        collection = load_feature_collection(FEATURES_PATH)

        self.assertEqual(collection.type, "FeatureCollection")
        self.assertGreaterEqual(len(collection.features), 20)

    def test_every_feature_has_required_safety_and_sources(self) -> None:
        collection = load_feature_collection(FEATURES_PATH)

        for feature in collection.features:
            with self.subTest(feature=feature.properties.id):
                self.assertTrue(feature.properties.safety_classification)
                self.assertGreaterEqual(len(feature.properties.source_ids), 1)
                self.assertTrue(feature.properties.summary)

    def test_known_feature_can_be_found_by_id(self) -> None:
        collection = load_feature_collection(FEATURES_PATH)
        feature = get_feature_by_id(collection, "city_hall_station")

        self.assertIsNotNone(feature)
        self.assertEqual(feature.properties.name, "City Hall Station")
        self.assertEqual(feature.properties.closed_year, 1945)


if __name__ == "__main__":
    unittest.main()

