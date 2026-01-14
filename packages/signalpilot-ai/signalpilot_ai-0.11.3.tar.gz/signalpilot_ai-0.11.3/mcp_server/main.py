"""FastAPI entrypoint for MCP tools."""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

from mcp_server.namespaces.terminal.router import router as terminal_router

try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except ImportError:
    pass

app = FastAPI(title="Sage MCP Server")

app.include_router(terminal_router, prefix="/terminal", tags=["terminal"])

mcp = FastApiMCP(app)

# Mount the MCP server directly to your FastAPI app
mcp.mount()
