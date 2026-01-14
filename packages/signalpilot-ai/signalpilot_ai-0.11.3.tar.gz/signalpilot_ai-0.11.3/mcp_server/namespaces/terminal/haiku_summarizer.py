"""Terminal-focused summarizer built on the generic agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from mcp_server.agent.generic_agent import AgentMessage, GenericAgent


@dataclass(frozen=True)
class HaikuSummary:
    text: str
    model: str = "haiku-4.5"


class HaikuSummarizer:
    """Summarizes terminal command output via the generic agent."""

    def __init__(self, agent: Optional[GenericAgent] = None) -> None:
        self.agent = agent or GenericAgent()

    async def summarize(
        self,
        *,
        command: str,
        summary_hint: Optional[str],
        output: str,
        exit_code: int,
        system_prompt: Optional[str] = None,
    ) -> Optional[HaikuSummary]:
        prompt = system_prompt or "Summarize tool output for downstream use."
        summary_text = summary_hint.strip() if summary_hint else ""
        message_lines = [
            f"Command: {command}",
            f"Exit code: {exit_code}",
        ]
        if summary_text:
            message_lines.append(f"Intent: {summary_text}")
        if output.strip():
            message_lines.append(f"Output:\n{output.strip()}")

        response = await self.agent.run(
            system_prompt=prompt,
            messages=[AgentMessage(role="user", content="\n".join(message_lines))],
        )
        if not response or self.agent.is_stub:
            return None
        return HaikuSummary(text=response.text, model=response.model)
