from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .config import SquadConfig, resolve_config
from .tools import register_tools


def build_server(config: SquadConfig | None = None) -> FastMCP:
    resolved = config or resolve_config()
    mcp = FastMCP("agent-code-squad")
    register_tools(mcp, config=resolved)
    return mcp
