from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.geo.features import load_feature_collection


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCES_DIR = REPO_ROOT / "data" / "sources"
MANIFEST_PATH = SOURCES_DIR / "source_manifest.json"
FEATURES_PATH = REPO_ROOT / "data" / "features" / "features.geojson"


class SourceCorpusTest(unittest.TestCase):
    def test_manifest_entries_point_to_existing_markdown_files(self) -> None:
        manifest = _load_manifest()

        for source in manifest["sources"]:
            with self.subTest(source=source["id"]):
                path = REPO_ROOT / source["local_path"]
                self.assertTrue(path.exists(), f"missing source file: {path}")
                text = path.read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---\n"))
                self.assertIn(f"document_id: {source['id']}", text)

    def test_feature_source_ids_resolve_to_manifest_entries(self) -> None:
        manifest = _load_manifest()
        manifest_ids = {source["id"] for source in manifest["sources"]}
        collection = load_feature_collection(FEATURES_PATH)

        for feature in collection.features:
            for source_id in feature.properties.source_ids:
                with self.subTest(feature=feature.properties.id, source=source_id):
                    self.assertIn(source_id, manifest_ids)

    def test_source_frontmatter_contains_feature_ids(self) -> None:
        manifest = _load_manifest()

        for source in manifest["sources"]:
            text = (REPO_ROOT / source["local_path"]).read_text(encoding="utf-8")
            with self.subTest(source=source["id"]):
                self.assertRegex(text, re.compile(r"^feature_ids: \[[^\]]+\]", re.MULTILINE))


def _load_manifest() -> dict[str, object]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
