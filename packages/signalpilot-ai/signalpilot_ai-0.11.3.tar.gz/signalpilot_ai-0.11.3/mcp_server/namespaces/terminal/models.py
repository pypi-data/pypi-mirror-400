"""Pydantic models for terminal tool inputs/outputs."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class TerminalExecuteCommandRequest(BaseModel):
    command: str = Field(..., description="Shell command to execute")
    summary: Optional[str] = Field(
        None,
        description=(
            "One sentence summary of what this command does. Used for logging or summaries."
        ),
    )
    timeout_seconds: int = Field(
        300,
        description="Command timeout in seconds (default: 300)",
        ge=1,
        le=3600,
    )


class TerminalExecuteCommandResponse(BaseModel):
    command: str = Field(..., description="Command that was executed.")
    stdout: str = Field(
        "",
        description="Stdout output (truncated to head/tail when output is large).",
    )
    stderr: str = Field(
        "",
        description="Stderr output (truncated to head/tail when output is large).",
    )
    exit_code: Optional[int] = Field(
        None,
        description="Exit code from the command process.",
    )
    output_truncated: bool = Field(
        False,
        description=(
            "True when total output exceeded 20 lines and the response uses "
            "head/tail truncation with a summary."
        ),
    )
    summary: Optional[str] = Field(
        None,
        description="Summary of the full output when total output exceeds 20 lines.",
    )
