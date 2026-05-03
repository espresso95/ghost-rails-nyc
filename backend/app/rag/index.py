from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from app.rag.documents import TextChunk, chunk_documents, load_source_documents


INDEX_FILENAME = "lexical_index.json"


@dataclass(frozen=True)
class IndexedChunk:
    chunk_id: str
    document_id: str
    title: str
    feature_ids: list[str]
    section_title: str
    text: str
    terms: dict[str, int]


@dataclass(frozen=True)
class LexicalIndex:
    index_type: str
    chunk_count: int
    document_count: int
    chunks: list[IndexedChunk]
    document_frequency: dict[str, int]

    def as_dict(self) -> dict[str, Any]:
        return {
            "index_type": self.index_type,
            "chunk_count": self.chunk_count,
            "document_count": self.document_count,
            "chunks": [asdict(chunk) for chunk in self.chunks],
            "document_frequency": self.document_frequency,
        }


def build_lexical_index(sources_path: Path, chunk_size_words: int = 140, overlap_words: int = 25) -> LexicalIndex:
    documents = load_source_documents(sources_path)
    chunks = chunk_documents(documents, chunk_size_words=chunk_size_words, overlap_words=overlap_words)
    indexed_chunks = [_index_chunk(chunk) for chunk in chunks]

    document_frequency: Counter[str] = Counter()
    for chunk in indexed_chunks:
        document_frequency.update(chunk.terms.keys())

    return LexicalIndex(
        index_type="local_lexical_v1",
        chunk_count=len(indexed_chunks),
        document_count=len(documents),
        chunks=indexed_chunks,
        document_frequency=dict(sorted(document_frequency.items())),
    )


def save_index(index: LexicalIndex, chroma_path: Path) -> Path:
    chroma_path.mkdir(parents=True, exist_ok=True)
    index_path = chroma_path / INDEX_FILENAME
    index_path.write_text(json.dumps(index.as_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return index_path


def load_index(chroma_path: Path) -> LexicalIndex:
    index_path = chroma_path / INDEX_FILENAME
    payload = json.loads(index_path.read_text(encoding="utf-8"))
    chunks = [IndexedChunk(**chunk) for chunk in payload["chunks"]]
    return LexicalIndex(
        index_type=payload["index_type"],
        chunk_count=payload["chunk_count"],
        document_count=payload["document_count"],
        chunks=chunks,
        document_frequency=payload["document_frequency"],
    )


def tokenize(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) > 1]


def score_chunk(index: LexicalIndex, chunk: IndexedChunk, query: str, selected_feature_id: str | None = None) -> float:
    query_terms = Counter(tokenize(query))
    if not query_terms:
        return 0.0

    score = 0.0
    total_chunks = max(1, index.chunk_count)
    for term, query_count in query_terms.items():
        term_frequency = chunk.terms.get(term, 0)
        if term_frequency == 0:
            continue
        inverse_document_frequency = math.log((1 + total_chunks) / (1 + index.document_frequency.get(term, 0))) + 1
        score += query_count * term_frequency * inverse_document_frequency

    if selected_feature_id and selected_feature_id in chunk.feature_ids:
        score *= 2.5

    return score


def _index_chunk(chunk: TextChunk) -> IndexedChunk:
    return IndexedChunk(
        chunk_id=chunk.chunk_id,
        document_id=chunk.document_id,
        title=chunk.title,
        feature_ids=chunk.feature_ids,
        section_title=chunk.section_title,
        text=chunk.text,
        terms=dict(Counter(tokenize(" ".join([chunk.title, chunk.section_title, chunk.text])))),
    )

