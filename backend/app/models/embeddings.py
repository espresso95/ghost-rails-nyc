from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence


@dataclass(frozen=True)
class EmbeddingResponse:
    embeddings: list[list[float]]
    provider: str
    model: str
    raw: Mapping[str, Any]


class EmbeddingModel(Protocol):
    provider: str
    model: str

    def embed(self, texts: Sequence[str]) -> EmbeddingResponse:
        ...

