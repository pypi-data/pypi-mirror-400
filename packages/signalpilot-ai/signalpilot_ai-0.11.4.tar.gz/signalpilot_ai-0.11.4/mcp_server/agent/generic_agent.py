"""Generic agent shim."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, Literal, Optional, Sequence, cast

AnthropicRole = Literal["user", "assistant"]


@dataclass(frozen=True)
class AgentMessage:
    role: str
    content: str


@dataclass(frozen=True)
class AgentResponse:
    text: str
    model: str


class GenericAgent:
    """Generic agent interface for tool output processing.

    The agent accepts a system prompt and chat history and returns a response
    string. Uses AsyncAnthropic for non-blocking API calls.
    """

    def __init__(self) -> None:
        self._model = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5")
        self._client = self._build_async_client()

    @property
    def is_stub(self) -> bool:
        return self._client is None

    async def run(
        self, *, system_prompt: str, messages: Iterable[AgentMessage]
    ) -> Optional[AgentResponse]:
        if not self._client:
            rendered = self._format_messages(system_prompt, messages)
            return AgentResponse(text=rendered, model="haiku-4.5")
        try:
            return await self._call_api(system_prompt, list(messages))
        except Exception:
            return None

    def _format_messages(
        self, system_prompt: str, messages: Iterable[AgentMessage]
    ) -> str:
        parts = [f"[system] {system_prompt.strip()}"]
        for message in messages:
            parts.append(f"[{message.role}] {message.content.strip()}")
        return "\n".join(parts).strip()

    def _build_async_client(self) -> Optional[object]:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return None
        try:
            import anthropic

            return anthropic.AsyncAnthropic(api_key=api_key)
        except ImportError:
            return None

    async def _call_api(
        self, system_prompt: str, messages: Sequence[AgentMessage]
    ) -> AgentResponse:
        from anthropic.types import MessageParam

        def _coerce_role(role: str) -> AnthropicRole:
            return "assistant" if role == "assistant" else "user"

        anthropic_messages: list[MessageParam] = [
            cast(
                MessageParam,
                {"role": _coerce_role(message.role), "content": message.content},
            )
            for message in messages
        ]
        response = await self._client.messages.create(  # type: ignore
            model=self._model,
            system=system_prompt,
            messages=anthropic_messages,
            max_tokens=512,
        )
        content = ""
        for block in response.content or []:
            if getattr(block, "type", None) == "text":
                content += getattr(block, "text", "")
        if not content:
            content = str(response)
        return AgentResponse(text=content.strip(), model=self._model)
