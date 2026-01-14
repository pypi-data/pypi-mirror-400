"""mcp-supervisor-squad MCP server package (supervisor-squad minimal workflow)."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("mcp-supervisor-squad")
except PackageNotFoundError:
    __version__ = "0.0.0"

from .server import APP_ID, build_server, run_server

__all__ = ["APP_ID", "build_server", "run_server"]
