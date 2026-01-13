"""LLM client wrapper."""

from __future__ import annotations

from typing import Any

from openai import OpenAI

from vision_agent.config import ModelConfig


class LlmClient:
    """Simple OpenAI-compatible client."""

    def __init__(self, settings: ModelConfig):
        self.settings = settings
        self.client = OpenAI(
            base_url=settings.base_url,
            api_key=settings.api_key,
        )

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        tool_choice: dict[str, Any] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ):
        """Send a chat completion request."""
        return self.client.chat.completions.create(
            model=self.settings.model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            temperature=(
                self.settings.temperature if temperature is None else temperature
            ),
            max_tokens=self.settings.max_tokens if max_tokens is None else max_tokens,
        )
