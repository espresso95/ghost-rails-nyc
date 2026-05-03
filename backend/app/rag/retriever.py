from __future__ import annotations

from dataclasses import dataclass

from app.rag.index import IndexedChunk, LexicalIndex, score_chunk


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: IndexedChunk
    score: float


def retrieve_chunks(
    index: LexicalIndex,
    query: str,
    selected_feature_id: str | None = None,
    top_k: int = 6,
) -> list[RetrievedChunk]:
    scored_chunks: list[RetrievedChunk] = []
    for chunk in index.chunks:
        score = score_chunk(index, chunk, query, selected_feature_id=selected_feature_id)
        if score > 0:
            scored_chunks.append(RetrievedChunk(chunk=chunk, score=score))

    scored_chunks.sort(key=lambda result: result.score, reverse=True)
    return scored_chunks[:top_k]

