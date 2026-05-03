from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.safety.policy import classify_question


class SafetyPolicyTest(unittest.TestCase):
    def test_blocks_access_instructions(self) -> None:
        decision = classify_question("Where is the access door and how do I avoid cameras?")

        self.assertFalse(decision.allowed)
        self.assertIn("access door", decision.matched_terms)
        self.assertIn("avoid cameras", decision.matched_terms)

    def test_allows_historical_question(self) -> None:
        decision = classify_question("Why did City Hall Station close?")

        self.assertTrue(decision.allowed)


if __name__ == "__main__":
    unittest.main()

