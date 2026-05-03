from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SourceDocument:
    document_id: str
    title: str
    source_type: str
    feature_ids: list[str]
    license_notes: str
    local_path: Path
    text: str


@dataclass(frozen=True)
class TextChunk:
    chunk_id: str
    document_id: str
    title: str
    feature_ids: list[str]
    section_title: str
    text: str
    start_word: int
    end_word: int


def load_source_documents(sources_path: Path) -> list[SourceDocument]:
    documents: list[SourceDocument] = []
    for path in sorted(sources_path.glob("*.md")):
        documents.append(load_source_document(path))
    return documents


def load_source_document(path: Path) -> SourceDocument:
    raw_text = path.read_text(encoding="utf-8")
    metadata, body = parse_frontmatter(raw_text)

    return SourceDocument(
        document_id=_required_string(metadata, "document_id", path),
        title=_required_string(metadata, "title", path),
        source_type=_required_string(metadata, "source_type", path),
        feature_ids=_required_string_list(metadata, "feature_ids", path),
        license_notes=_required_string(metadata, "license_notes", path),
        local_path=path,
        text=body.strip(),
    )


def parse_frontmatter(raw_text: str) -> tuple[dict[str, Any], str]:
    if not raw_text.startswith("---\n"):
        raise ValueError("source document is missing frontmatter")

    end_index = raw_text.find("\n---\n", 4)
    if end_index == -1:
        raise ValueError("source document frontmatter is not closed")

    metadata_text = raw_text[4:end_index]
    body = raw_text[end_index + 5 :]
    metadata: dict[str, Any] = {}

    for line in metadata_text.splitlines():
        if not line.strip():
            continue
        key, separator, value = line.partition(":")
        if separator == "":
            raise ValueError(f"invalid frontmatter line: {line}")
        metadata[key.strip()] = _parse_frontmatter_value(value.strip())

    return metadata, body


def chunk_document(document: SourceDocument, chunk_size_words: int = 140, overlap_words: int = 25) -> list[TextChunk]:
    sections = _split_sections(document.text)
    chunks: list[TextChunk] = []
    chunk_number = 0
    word_cursor = 0

    for section_title, section_text in sections:
        words = section_text.split()
        if not words:
            continue
        step = max(1, chunk_size_words - overlap_words)
        for start in range(0, len(words), step):
            end = min(len(words), start + chunk_size_words)
            chunk_words = words[start:end]
            if not chunk_words:
                continue
            chunk_number += 1
            chunks.append(
                TextChunk(
                    chunk_id=f"{document.document_id}__chunk_{chunk_number:04d}",
                    document_id=document.document_id,
                    title=document.title,
                    feature_ids=document.feature_ids,
                    section_title=section_title,
                    text=" ".join(chunk_words),
                    start_word=word_cursor + start,
                    end_word=word_cursor + end,
                )
            )
            if end == len(words):
                break
        word_cursor += len(words)

    return chunks


def chunk_documents(documents: list[SourceDocument], chunk_size_words: int = 140, overlap_words: int = 25) -> list[TextChunk]:
    chunks: list[TextChunk] = []
    for document in documents:
        chunks.extend(chunk_document(document, chunk_size_words=chunk_size_words, overlap_words=overlap_words))
    return chunks


def _split_sections(text: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, list[str]]] = []
    current_title = "Overview"
    current_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("#"):
            if current_lines:
                sections.append((current_title, current_lines))
            current_title = line.lstrip("#").strip() or "Untitled"
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_title, current_lines))

    return [(title, "\n".join(lines).strip()) for title, lines in sections if "\n".join(lines).strip()]


def _parse_frontmatter_value(value: str) -> str | list[str]:
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip("'\"") for item in inner.split(",")]
    return value.strip("'\"")


def _required_string(metadata: dict[str, Any], key: str, path: Path) -> str:
    value = metadata.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{path} frontmatter field {key} must be a string")
    return value


def _required_string_list(metadata: dict[str, Any], key: str, path: Path) -> list[str]:
    value = metadata.get(key)
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        raise ValueError(f"{path} frontmatter field {key} must be a non-empty string list")
    return value

