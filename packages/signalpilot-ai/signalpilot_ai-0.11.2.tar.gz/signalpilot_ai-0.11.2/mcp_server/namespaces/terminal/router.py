"""FastAPI router for terminal tools."""

from __future__ import annotations

from fastapi import APIRouter

from mcp_server.namespaces.terminal.models import (
    TerminalExecuteCommandRequest,
    TerminalExecuteCommandResponse,
)
from mcp_server.namespaces.terminal.service import get_terminal_service

router = APIRouter()


@router.post("/execute_command", name="terminal-execute_command")
async def execute_command(
    request: TerminalExecuteCommandRequest,
) -> TerminalExecuteCommandResponse:
    service = get_terminal_service()
    return await service.execute(request)
