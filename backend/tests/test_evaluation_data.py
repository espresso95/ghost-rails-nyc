from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


REPO_ROOT = Path(__file__).resolve().parents[2]
QUESTIONS_PATH = REPO_ROOT / "data" / "eval" / "questions.jsonl"


class EvaluationDataTest(unittest.TestCase):
    def test_questions_jsonl_is_valid(self) -> None:
        rows = []
        for line in QUESTIONS_PATH.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rows.append(json.loads(line))

        self.assertGreaterEqual(len(rows), 5)
        for row in rows:
            with self.subTest(question=row["id"]):
                self.assertIn("question", row)
                self.assertIn("expected_mode", row)
                self.assertIsInstance(row["required_terms"], list)


if __name__ == "__main__":
    unittest.main()
