from __future__ import annotations

from app.geo.features import RailFeature
from app.rag.retriever import RetrievedChunk


def build_context_prompt(question: str, selected_feature: RailFeature | None, results: list[RetrievedChunk]) -> str:
    feature_context = "No selected feature."
    if selected_feature:
        properties = selected_feature.properties
        feature_context = "\n".join(
            [
                f"Name: {properties.name}",
                f"Type: {properties.feature_type}",
                f"Borough: {properties.borough}",
                f"Status: {properties.status}",
                f"Safety: {properties.safety_classification}",
                f"Summary: {properties.summary}",
            ]
        )

    snippets = []
    for result in results:
        snippets.append(
            "\n".join(
                [
                    f"Source: {result.chunk.title}",
                    f"Chunk: {result.chunk.chunk_id}",
                    result.chunk.text,
                ]
            )
        )

    return "\n\n".join(
        [
            "Selected feature:",
            feature_context,
            "Retrieved source snippets:",
            "\n\n".join(snippets),
            "User question:",
            question,
        ]
    )

