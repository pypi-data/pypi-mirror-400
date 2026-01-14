"""FastMCP server definition (supervisor-squad minimal workflow)."""

from __future__ import annotations

from typing import Any, cast

from mcp.server.fastmcp import FastMCP

from .persistence.state import RunStore
from .runtime.worker import Worker

APP_ID = "mcp-supervisor-squad"


def build_server() -> FastMCP:
    server = FastMCP(APP_ID)
    store = RunStore()
    worker = Worker(store)

    @server.tool(name="squad_start")
    def squad_start(cwd: str, query: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
        state = worker.start(cwd=cwd, query=query, options=cast(dict[str, Any], options or {}))
        payload = state.public_status()
        store.save(state)
        return payload

    @server.tool(name="squad_status")
    def squad_status(run_id: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
        resolved_options = cast(dict[str, Any], options or {})
        state = store.load(run_id, cwd=resolved_options.get("cwd") if isinstance(resolved_options.get("cwd"), str) else None)
        payload = state.public_status(options=resolved_options)
        # Persist brief cache updates (low-IO, single file write).
        store.save(state)
        return payload

    @server.tool(name="squad_apply")
    def squad_apply(run_id: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
        resolved_options = cast(dict[str, Any], options or {})
        state = store.load(run_id, cwd=resolved_options.get("cwd") if isinstance(resolved_options.get("cwd"), str) else None)
        return worker.apply(state, options=resolved_options)

    return server


def run_server(*, transport: str = "stdio") -> None:
    if transport != "stdio":
        raise ValueError(f"Unsupported transport '{transport}'.")
    server = build_server()
    server.run(transport=transport)
