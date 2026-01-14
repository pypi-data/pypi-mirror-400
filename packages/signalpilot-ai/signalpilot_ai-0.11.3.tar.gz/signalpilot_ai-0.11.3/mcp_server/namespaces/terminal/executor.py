"""Terminal command execution helpers."""

from __future__ import annotations

import asyncio
import os
import signal
from dataclasses import dataclass
from typing import Optional

MAX_OUTPUT_BYTES = 10 * 1024 * 1024  # 10 MB cap per stream


@dataclass(frozen=True)
class CommandResult:
    stdout: str
    stderr: str
    exit_code: int


class TerminalCommandExecutor:
    """Executes shell commands with timeout and captures output."""

    def __init__(self, cwd: Optional[str] = None) -> None:
        self.cwd = cwd or os.getcwd()

    async def run(self, command: str, timeout_seconds: int) -> CommandResult:
        process = await asyncio.create_subprocess_shell(
            command,
            cwd=self.cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            start_new_session=True,
        )
        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout_seconds,
            )
            stdout = self._decode_limited(stdout_bytes)
            stderr = self._decode_limited(stderr_bytes)
            return CommandResult(
                stdout=stdout,
                stderr=stderr,
                exit_code=process.returncode or 0,
            )
        except asyncio.TimeoutError:
            self._kill_process_tree(process.pid)
            stdout = self._decode_limited(await self._read_limited(process.stdout))
            stderr = self._decode_limited(await self._read_limited(process.stderr))
            message = f"Command timed out after {timeout_seconds} seconds."
            stderr = f"{stderr}\n{message}" if stderr else message
            return CommandResult(stdout=stdout, stderr=stderr, exit_code=124)
        except Exception as exc:
            self._kill_process_tree(process.pid)
            return CommandResult(
                stdout="",
                stderr=f"Command execution failed: {exc}",
                exit_code=1,
            )

    def _decode_limited(self, data: Optional[bytes]) -> str:
        """Decode bytes to string with size limit."""
        if not data:
            return ""
        return data[:MAX_OUTPUT_BYTES].decode(errors="replace")

    async def _read_limited(
        self, stream: Optional[asyncio.StreamReader]
    ) -> bytes:
        """Read from async stream with size limit."""
        if stream is None:
            return b""
        try:
            return await stream.read(MAX_OUTPUT_BYTES)
        except Exception:
            return b""

    def _kill_process_tree(self, pid: Optional[int]) -> None:
        """Kill the process and all its children via process group."""
        if pid is None:
            return
        try:
            os.killpg(os.getpgid(pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError, OSError):
            pass
