from __future__ import annotations

from typing import Sequence

from app.config import ChatModelSettings
from app.models.chat import ChatMessage, ChatOptions, ChatResponse
from app.models.errors import ModelProviderError
from app.models.providers.http import post_json


class GroqChatModel:
    provider = "groq"

    def __init__(self, settings: ChatModelSettings) -> None:
        if not settings.api_key:
            raise ValueError("GROQ_API_KEY or GHOST_RAILS_CHAT_API_KEY is required for Groq chat")
        self.settings = settings
        self.model = settings.model
        self.base_url = settings.base_url.rstrip("/")
        self.api_key = settings.api_key

    def complete(self, messages: Sequence[ChatMessage], options: ChatOptions | None = None) -> ChatResponse:
        options = options or ChatOptions()
        payload = {
            "model": self.model,
            "messages": [message.as_dict() for message in messages],
            "temperature": self.settings.temperature if options.temperature is None else options.temperature,
            "max_tokens": self.settings.max_output_tokens
            if options.max_output_tokens is None
            else options.max_output_tokens,
        }
        response = post_json(
            f"{self.base_url}/chat/completions",
            payload,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout_seconds=self.settings.timeout_seconds,
            label="Groq chat",
        )
        text = _extract_openai_compatible_text(response)
        return ChatResponse(text=text, provider=self.provider, model=self.model, raw=response)


def _extract_openai_compatible_text(response: object) -> str:
    if not isinstance(response, dict):
        raise ModelProviderError("Groq chat returned an unexpected response")
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ModelProviderError("Groq chat returned no choices")
    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        raise ModelProviderError("Groq chat returned an invalid choice")
    message = first_choice.get("message")
    if not isinstance(message, dict) or not isinstance(message.get("content"), str):
        raise ModelProviderError("Groq chat returned no message content")
    return message["content"]

