from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.rag.index import INDEX_FILENAME, build_lexical_index, load_index, save_index
from app.rag.retriever import retrieve_chunks


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCES_PATH = REPO_ROOT / "data" / "sources"


class RagIndexTest(unittest.TestCase):
    def test_builds_index_from_local_sources(self) -> None:
        index = build_lexical_index(SOURCES_PATH)

        self.assertEqual(index.index_type, "local_lexical_v1")
        self.assertGreaterEqual(index.document_count, 8)
        self.assertGreaterEqual(index.chunk_count, 8)
        self.assertIn("city", index.document_frequency)

    def test_saves_and_loads_index(self) -> None:
        index = build_lexical_index(SOURCES_PATH)

        with tempfile.TemporaryDirectory() as directory:
            output_path = save_index(index, Path(directory))
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            loaded = load_index(Path(directory))

        self.assertEqual(output_path.name, INDEX_FILENAME)
        self.assertEqual(payload["index_type"], "local_lexical_v1")
        self.assertEqual(loaded.chunk_count, index.chunk_count)

    def test_retrieves_relevant_city_hall_chunk(self) -> None:
        index = build_lexical_index(SOURCES_PATH)
        results = retrieve_chunks(index, "Why did City Hall Station close?", selected_feature_id="city_hall_station")

        self.assertGreaterEqual(len(results), 1)
        top_chunk = results[0].chunk
        self.assertIn("city_hall_station", top_chunk.feature_ids)
        self.assertIn("City Hall", top_chunk.text)


if __name__ == "__main__":
    unittest.main()

