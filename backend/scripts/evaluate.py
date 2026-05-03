from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path

from app.config import load_settings
from app.geo.features import load_feature_collection
from app.rag.answer import answer_question


@dataclass(frozen=True)
class EvaluationQuestion:
    id: str
    question: str
    selected_feature_id: str | None
    expected_mode: str
    required_terms: list[str]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic Ghost Rails RAG evaluation.")
    parser.add_argument("--questions", type=Path, default=Path("../data/eval/questions.jsonl"))
    args = parser.parse_args()

    settings = load_settings()
    features = load_feature_collection(settings.features_path)
    questions = load_questions(args.questions)
    failures: list[str] = []

    for item in questions:
        started_at = time.perf_counter()
        answer = answer_question(
            question=item.question,
            selected_feature_id=item.selected_feature_id,
            settings=settings,
            features=features,
        )
        latency_ms = round((time.perf_counter() - started_at) * 1000, 1)
        text = answer.answer.lower()
        if item.expected_mode == "refusal" and "cannot help" not in text:
            failures.append(f"{item.id}: expected refusal")
        for term in item.required_terms:
            if term.lower() not in text:
                failures.append(f"{item.id}: missing required term {term}")
        chunk_ids = answer.retrieval_debug.get("retrieved_chunk_ids", [])
        print(f"{item.id}: {answer.confidence} {latency_ms}ms chunks={chunk_ids} {answer.answer[:160]}")

    if failures:
        print("Evaluation failures:")
        for failure in failures:
            print(failure)
        raise SystemExit(1)

    print(f"Evaluation passed: {len(questions)} questions")


def load_questions(path: Path) -> list[EvaluationQuestion]:
    questions: list[EvaluationQuestion] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        questions.append(EvaluationQuestion(**payload))
    return questions


if __name__ == "__main__":
    main()
