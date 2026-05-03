from __future__ import annotations

from dataclasses import dataclass


UNSAFE_TERMS = [
    "access door",
    "alarm",
    "avoid cameras",
    "avoid police",
    "break in",
    "bypass",
    "climb fence",
    "emergency exit",
    "enter tunnel",
    "get inside",
    "get into",
    "sneak",
    "trespass",
    "urban exploration",
]


@dataclass(frozen=True)
class SafetyDecision:
    allowed: bool
    reason: str | None = None
    matched_terms: list[str] | None = None


def classify_question(question: str) -> SafetyDecision:
    normalized = question.lower()
    matched_terms = [term for term in UNSAFE_TERMS if term in normalized]
    if matched_terms:
        return SafetyDecision(
            allowed=False,
            reason="Restricted-access request blocked by safety policy.",
            matched_terms=matched_terms,
        )
    return SafetyDecision(allowed=True, matched_terms=[])

