from __future__ import annotations

from typing import Sequence
from urllib.parse import quote

from app.config import ChatModelSettings
from app.models.chat import ChatMessage, ChatOptions, ChatResponse
from app.models.errors import ModelProviderError
from app.models.providers.http import post_json


class GeminiChatModel:
    provider = "gemini"

    def __init__(self, settings: ChatModelSettings) -> None:
        if not settings.api_key:
            raise ValueError("GEMINI_API_KEY or GHOST_RAILS_CHAT_API_KEY is required for Gemini chat")
        self.settings = settings
        self.model = settings.model
        self.base_url = settings.base_url.rstrip("/")
        self.api_key = settings.api_key

    def complete(self, messages: Sequence[ChatMessage], options: ChatOptions | None = None) -> ChatResponse:
        options = options or ChatOptions()
        system_text = "\n\n".join(message.content for message in messages if message.role == "system")
        contents = [_gemini_content(message) for message in messages if message.role != "system"]
        payload: dict[str, object] = {
            "contents": contents,
            "generationConfig": {
                "temperature": self.settings.temperature if options.temperature is None else options.temperature,
                "maxOutputTokens": self.settings.max_output_tokens
                if options.max_output_tokens is None
                else options.max_output_tokens,
            },
        }
        if system_text:
            payload["systemInstruction"] = {"parts": [{"text": system_text}]}

        response = post_json(
            f"{self.base_url}/models/{quote(self.model, safe='')}:generateContent?key={quote(self.api_key, safe='')}",
            payload,
            timeout_seconds=self.settings.timeout_seconds,
            label="Gemini chat",
        )
        text = _extract_gemini_text(response)
        return ChatResponse(text=text, provider=self.provider, model=self.model, raw=response)


def _gemini_content(message: ChatMessage) -> dict[str, object]:
    role = "model" if message.role == "assistant" else "user"
    return {"role": role, "parts": [{"text": message.content}]}


def _extract_gemini_text(response: object) -> str:
    if not isinstance(response, dict):
        raise ModelProviderError("Gemini chat returned an unexpected response")
    candidates = response.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ModelProviderError("Gemini chat returned no candidates")
    first_candidate = candidates[0]
    if not isinstance(first_candidate, dict):
        raise ModelProviderError("Gemini chat returned an invalid candidate")
    content = first_candidate.get("content")
    if not isinstance(content, dict):
        raise ModelProviderError("Gemini chat returned no content")
    parts = content.get("parts")
    if not isinstance(parts, list):
        raise ModelProviderError("Gemini chat returned no text parts")
    text_parts = [part.get("text") for part in parts if isinstance(part, dict) and isinstance(part.get("text"), str)]
    if not text_parts:
        raise ModelProviderError("Gemini chat returned no text")
    return "".join(text_parts)

