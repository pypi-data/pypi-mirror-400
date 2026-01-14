"""mcp-supervisor-squad MCP server package (supervisor-squad minimal workflow)."""

__version__ = "0.1.2"

from .server import APP_ID, build_server, run_server

__all__ = ["APP_ID", "build_server", "run_server"]
