"""Terminal tool service with output summarization."""

from __future__ import annotations

from typing import Optional

from mcp_server.namespaces.terminal.haiku_summarizer import HaikuSummarizer
from mcp_server.namespaces.terminal.executor import (
    CommandResult,
    TerminalCommandExecutor,
)
from mcp_server.namespaces.terminal.models import (
    TerminalExecuteCommandRequest,
    TerminalExecuteCommandResponse,
)


class TerminalCommandService:
    """Coordinates execution and summarization."""

    def __init__(
        self,
        *,
        executor: Optional[TerminalCommandExecutor] = None,
        summarizer: Optional[HaikuSummarizer] = None,
        max_output_lines: int = 20,
        head_lines: int = 10,
        tail_lines: int = 10,
    ) -> None:
        self.executor = executor or TerminalCommandExecutor()
        self.summarizer = summarizer or HaikuSummarizer()
        self.max_output_lines = max_output_lines
        self.head_lines = head_lines
        self.tail_lines = tail_lines

    async def execute(
        self, request: TerminalExecuteCommandRequest
    ) -> TerminalExecuteCommandResponse:
        result = await self.executor.run(request.command, request.timeout_seconds)
        stdout = result.stdout
        stderr = result.stderr
        output_truncated = False
        summary_text: Optional[str] = None

        total_lines = self._line_count(stdout) + self._line_count(stderr)
        should_summarize = total_lines > self.max_output_lines

        if should_summarize:
            stdout, stdout_truncated = self._truncate_output(stdout)
            stderr, stderr_truncated = self._truncate_output(stderr)
            output_truncated = True
            summary_text = await self._summarize(
                request, result, stdout_truncated or stderr_truncated
            )

        return TerminalExecuteCommandResponse(
            command=request.command,
            stdout=stdout,
            stderr=stderr,
            exit_code=result.exit_code,
            output_truncated=output_truncated,
            summary=summary_text,
        )

    def _line_count(self, text: str) -> int:
        if not text:
            return 0
        return len(text.splitlines())

    def _truncate_output(self, text: str) -> tuple[str, bool]:
        if not text:
            return "", False

        lines = text.splitlines()
        if len(lines) <= self.max_output_lines:
            return text, False

        head = lines[: self.head_lines]
        tail = lines[-self.tail_lines :]
        middle_count = len(lines) - self.head_lines - self.tail_lines
        truncated = "\n".join(head + [f"... {middle_count} lines truncated ..."] + tail)
        return truncated, True

    async def _summarize(
        self,
        request: TerminalExecuteCommandRequest,
        result: CommandResult,
        truncated: bool,
    ) -> str:
        system_prompt = (
            "You are summarizing terminal command output for another agent. "
            "Return a concise, information-dense summary that preserves all "
            "critical details. Include: command intent (if provided), exit "
            "status, key stdout/stderr highlights, any errors with likely "
            "cause from logs, files/paths or resources touched, counts or "
            "metrics, and note if output was truncated. Prefer 3-5 short "
            "sentences or bullet-like lines; avoid generic phrasing."
        )
        combined_output = "\n".join(
            [chunk for chunk in (result.stdout, result.stderr) if chunk]
        )
        if truncated:
            combined_output = f"[Output truncated]\n{combined_output}"
        summary = await self.summarizer.summarize(
            command=request.command,
            summary_hint=request.summary,
            output=combined_output,
            exit_code=result.exit_code,
            system_prompt=system_prompt,
        )
        if summary:
            return summary.text

        status = "succeeded" if result.exit_code == 0 else "failed"
        stdout_lines = self._line_count(result.stdout)
        stderr_lines = self._line_count(result.stderr)
        base = (
            f"Command {status} with exit code {result.exit_code}. "
            f"Stdout lines: {stdout_lines}; stderr lines: {stderr_lines}."
        )
        if truncated:
            base = f"{base} Output truncated to head/tail lines."
        if request.summary:
            return f"{request.summary} {base}"
        return base


_terminal_service: Optional[TerminalCommandService] = None


def get_terminal_service() -> TerminalCommandService:
    global _terminal_service
    if _terminal_service is None:
        _terminal_service = TerminalCommandService()
    return _terminal_service
