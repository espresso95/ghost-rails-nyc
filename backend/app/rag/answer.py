from __future__ import annotations

from dataclasses import dataclass

from app.config import AppSettings
from app.geo.features import FeatureCollection, RailFeature, get_feature_by_id
from app.models.chat import ChatMessage
from app.models.errors import ModelProviderError
from app.models.factory import build_chat_model
from app.rag.index import build_lexical_index, load_index, save_index
from app.rag.prompts import build_context_prompt
from app.rag.retriever import RetrievedChunk, retrieve_chunks
from app.safety.policy import SafetyDecision, classify_question


@dataclass(frozen=True)
class SourceSnippet:
    title: str
    document_id: str
    chunk_id: str
    snippet: str

    def as_dict(self) -> dict[str, str]:
        return {
            "title": self.title,
            "document_id": self.document_id,
            "chunk_id": self.chunk_id,
            "snippet": self.snippet,
        }


@dataclass(frozen=True)
class ChatAnswer:
    answer: str
    sources: list[SourceSnippet]
    confidence: str
    safety_note: str | None
    retrieval_debug: dict[str, object]

    def as_dict(self) -> dict[str, object]:
        return {
            "answer": self.answer,
            "sources": [source.as_dict() for source in self.sources],
            "confidence": self.confidence,
            "safety_note": self.safety_note,
            "retrieval_debug": self.retrieval_debug,
        }


def answer_question(
    question: str,
    selected_feature_id: str | None,
    settings: AppSettings,
    features: FeatureCollection,
    include_sources: bool = True,
) -> ChatAnswer:
    selected_feature = get_feature_by_id(features, selected_feature_id) if selected_feature_id else None
    safety_decision = classify_question(question)
    if not safety_decision.allowed:
        return _safety_refusal(safety_decision, selected_feature)

    index = _load_or_build_index(settings)
    retrieval_results = retrieve_chunks(
        index,
        question,
        selected_feature_id=selected_feature_id,
        top_k=settings.retrieval.similarity_top_k,
    )
    final_results = retrieval_results[: settings.retrieval.context_chunks]

    if not final_results:
        return ChatAnswer(
            answer="The local corpus does not contain enough evidence to answer that.",
            sources=[],
            confidence="low",
            safety_note=_feature_safety_note(selected_feature),
            retrieval_debug={"top_k": settings.retrieval.similarity_top_k, "used_chunks": 0},
        )

    sources = _source_snippets(final_results) if include_sources else []
    answer = _grounded_fallback_answer(question, selected_feature, final_results)
    confidence = "high" if selected_feature and any(selected_feature.properties.id in result.chunk.feature_ids for result in final_results) else "medium"

    if settings.enable_llm_answers:
        answer = _try_llm_answer(settings, question, selected_feature, final_results, fallback_answer=answer)

    return ChatAnswer(
        answer=answer,
        sources=sources,
        confidence=confidence,
        safety_note=_feature_safety_note(selected_feature),
        retrieval_debug={
            "top_k": settings.retrieval.similarity_top_k,
            "used_chunks": len(final_results),
            "retrieved_chunk_ids": [result.chunk.chunk_id for result in retrieval_results],
            "answer_mode": "llm" if settings.enable_llm_answers else "local_grounded_fallback",
        },
    )


def _load_or_build_index(settings: AppSettings):
    try:
        return load_index(settings.chroma_path)
    except FileNotFoundError:
        index = build_lexical_index(settings.sources_path)
        save_index(index, settings.chroma_path)
        return index


def _grounded_fallback_answer(
    question: str,
    selected_feature: RailFeature | None,
    results: list[RetrievedChunk],
) -> str:
    subject = selected_feature.properties.name if selected_feature else "the question"
    lead = f"The local corpus has relevant notes for {subject}."
    if "why" in question.lower() and selected_feature:
        lead = f"The local corpus points to the historical context for why {selected_feature.properties.name} changed or closed."

    supporting_sentences = []
    for result in results:
        sentence = _first_sentence(result.chunk.text)
        if sentence:
            supporting_sentences.append(sentence)

    if not supporting_sentences:
        return "The local corpus has relevant chunks, but they do not contain enough readable evidence to form an answer."

    return " ".join([lead, *supporting_sentences[:3]])


def _try_llm_answer(
    settings: AppSettings,
    question: str,
    selected_feature: RailFeature | None,
    results: list[RetrievedChunk],
    fallback_answer: str,
) -> str:
    prompt = build_context_prompt(question, selected_feature, results)
    try:
        chat_model = build_chat_model(settings)
        response = chat_model.complete(
            [
                ChatMessage(
                    role="system",
                    content="Answer only using the provided Ghost Rails NYC context. Refuse restricted-access guidance.",
                ),
                ChatMessage(role="user", content=prompt),
            ]
        )
    except (ModelProviderError, ValueError):
        return fallback_answer
    return response.text.strip() or fallback_answer


def _source_snippets(results: list[RetrievedChunk]) -> list[SourceSnippet]:
    snippets: list[SourceSnippet] = []
    for result in results:
        snippets.append(
            SourceSnippet(
                title=result.chunk.title,
                document_id=result.chunk.document_id,
                chunk_id=result.chunk.chunk_id,
                snippet=result.chunk.text[:500],
            )
        )
    return snippets


def _safety_refusal(decision: SafetyDecision, selected_feature: RailFeature | None) -> ChatAnswer:
    subject = selected_feature.properties.name if selected_feature else "that infrastructure"
    return ChatAnswer(
        answer=(
            f"I cannot help with entering, accessing, bypassing security for, or exploring restricted transit infrastructure at {subject}. "
            "I can help with safe historical context, public map context, museum information, official tours, or legally viewable remnants when the local corpus supports it."
        ),
        sources=[],
        confidence="high",
        safety_note=decision.reason,
        retrieval_debug={"blocked_by_safety": True, "matched_terms": decision.matched_terms},
    )


def _feature_safety_note(feature: RailFeature | None) -> str | None:
    if feature is None:
        return None
    classification = feature.properties.safety_classification
    if classification == "do_not_access":
        return "This feature is marked do_not_access. Use historical context only."
    if classification == "museum_or_official_tour":
        return "This feature should be discussed through museum or official-tour context when supported."
    if classification == "public_view_only":
        return "Use only public, legal viewpoints for this feature."
    return None


def _first_sentence(text: str) -> str:
    for separator in [". ", "? ", "! "]:
        if separator in text:
            return text.split(separator, 1)[0].strip() + separator.strip()
    return text.strip()

