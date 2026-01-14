"""FastMCP server definition (supervisor-squad minimal workflow)."""

from __future__ import annotations

import time
from typing import Any, cast

from mcp.server.fastmcp import FastMCP

from .persistence.state import RunStore
from .runtime.worker import Worker

APP_ID = "mcp-supervisor-squad"


def build_server() -> FastMCP:
    server = FastMCP(APP_ID)
    store = RunStore()
    worker = Worker(store)

    def _require_cwd(options: dict[str, Any] | None) -> str:
        if not isinstance(options, dict):
            raise ValueError("options must be an object (dict) like {\"cwd\": \"/abs/path/in/repo\"}.")
        cwd = options.get("cwd")
        if not isinstance(cwd, str) or not cwd.strip():
            raise ValueError("options.cwd is required and must be an absolute path inside the target repo.")
        if not cwd.startswith("/"):
            raise ValueError("options.cwd must be an absolute path (e.g. /Volumes/.../repo).")
        return cwd

    @server.tool(name="squad_start")
    def squad_start(cwd: str, query: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
        opt = cast(dict[str, Any], options or {})
        state = worker.start(cwd=cwd, query=query, options=opt)
        payload = state.public_status(options=opt)
        store.save(state)
        return payload

    @server.tool(name="squad_status")
    def squad_status(run_id: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
        resolved_options = cast(dict[str, Any], options or {})
        try:
            cwd = _require_cwd(resolved_options)
        except Exception as exc:
            return {
                "run_id": run_id,
                "next_action": "wait",
                "forced_wait_ms": 60000,
                "wait_reason": "error",
                "has_update": False,
                "event_id": -1,
                "summary": [
                    "错误: squad_status 需要 options.cwd（绝对路径）",
                    "示例: options={\"cwd\":\"/Volumes/workspace/.../<repo>\"}",
                    f"原因: {str(exc)[:120]}",
                ],
            }
        if bool(resolved_options.get("cancel")):
            try:
                _ = worker.cancel(
                    run_id=run_id,
                    cwd=cwd,
                    reason=str(resolved_options.get("cancel_reason") or "").strip() or None,
                )
            except Exception:
                pass
            # Return immediately after cancellation; do not enforce wait.
            try:
                state = store.load(run_id, cwd=cwd)
                return state.public_status(options=resolved_options)
            except Exception as exc:
                return {
                    "run_id": run_id,
                    "next_action": "wait",
                    "forced_wait_ms": 60000,
                    "wait_reason": "error",
                    "has_update": False,
                    "event_id": -1,
                    "summary": [
                        "错误: 取消后无法读取 run（请确认 run_id 与 cwd 匹配）",
                        "参考: <repo_root>/.codex/supervisor-squad/contract.json",
                        f"原因: {str(exc)[:120]}",
                    ],
                }
        try:
            state = store.load(run_id, cwd=cwd)
        except Exception as exc:
            return {
                "run_id": run_id,
                "next_action": "wait",
                "forced_wait_ms": 60000,
                "wait_reason": "error",
                "has_update": False,
                "event_id": -1,
                "summary": [
                    "错误: 找不到 run（请确认 run_id 与 cwd 匹配）",
                    "参考: <repo_root>/.codex/supervisor-squad/contract.json",
                    f"原因: {str(exc)[:120]}",
                ],
            }
        payload = state.public_status(options=resolved_options)
        store.save(state)
        return payload

    @server.tool(name="squad_apply")
    def squad_apply(run_id: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
        resolved_options = cast(dict[str, Any], options or {})
        try:
            cwd = _require_cwd(resolved_options)
        except Exception as exc:
            return {
                "run_id": run_id,
                "next_action": "wait",
                "forced_wait_ms": 60000,
                "wait_reason": "error",
                "has_update": False,
                "event_id": -1,
                "summary": [
                    "错误: squad_apply 需要 options.cwd（绝对路径）",
                    "示例: options={\"cwd\":\"/Volumes/workspace/.../<repo>\",\"dry_run\":true}",
                    f"原因: {str(exc)[:120]}",
                ],
                "applied": False,
                "dry_run": True,
                "summary": "",
                "error": "missing options.cwd",
            }
        try:
            state = store.load(run_id, cwd=cwd)
        except Exception as exc:
            return {
                "run_id": run_id,
                "next_action": "wait",
                "forced_wait_ms": 60000,
                "wait_reason": "error",
                "has_update": False,
                "event_id": -1,
                "summary": [
                    "错误: 找不到 run（请确认 run_id 与 cwd 匹配）",
                    "参考: <repo_root>/.codex/supervisor-squad/contract.json",
                    f"原因: {str(exc)[:120]}",
                ],
                "applied": False,
                "dry_run": bool(resolved_options.get("dry_run", True)),
                "summary": "",
                "error": str(exc)[:200],
            }
        return worker.apply(state, options=resolved_options)

    return server


def run_server(*, transport: str = "stdio") -> None:
    if transport != "stdio":
        raise ValueError(f"Unsupported transport '{transport}'.")
    server = build_server()
    server.run(transport=transport)
