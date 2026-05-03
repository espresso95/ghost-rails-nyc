from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str

    def as_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass(frozen=True)
class ChatOptions:
    temperature: float | None = None
    max_output_tokens: int | None = None


@dataclass(frozen=True)
class ChatResponse:
    text: str
    provider: str
    model: str
    raw: Mapping[str, Any]


class ChatModel(Protocol):
    provider: str
    model: str

    def complete(self, messages: Sequence[ChatMessage], options: ChatOptions | None = None) -> ChatResponse:
        ...

