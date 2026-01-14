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
        state = worker.start(cwd=cwd, query=query, options=cast(dict[str, Any], options or {}))
        payload = state.public_status()
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
                "recommended_poll_ms": 60000,
                "wait_reason": "error",
                "lines": [
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
                    "recommended_poll_ms": 60000,
                    "wait_reason": "error",
                    "lines": [
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
                "recommended_poll_ms": 60000,
                "wait_reason": "error",
                "lines": [
                    "错误: 找不到 run（请确认 run_id 与 cwd 匹配）",
                    "参考: <repo_root>/.codex/supervisor-squad/contract.json",
                    f"原因: {str(exc)[:120]}",
                ],
            }
        before = state.brief_cache.generated_at if state.brief_cache else None
        payload = state.public_status(options=resolved_options)
        after = state.brief_cache.generated_at if state.brief_cache else None

        # Enforce the tool-provided polling interval server-side to reduce chat/context churn.
        # If called again before the cached brief expires, block until it does (capped at 60s),
        # then recompute status once.
        if before == after:
            wait_ms = int(payload.get("recommended_poll_ms") or 0)
            wait_ms = max(0, min(wait_ms, 60_000))
            if wait_ms >= 1000:
                time.sleep(wait_ms / 1000.0)
                state = store.load(run_id, cwd=cwd)
                before = state.brief_cache.generated_at if state.brief_cache else None
                payload = state.public_status(options=resolved_options)
                after = state.brief_cache.generated_at if state.brief_cache else None

        if before != after:
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
                "recommended_poll_ms": 60000,
                "wait_reason": "error",
                "lines": [
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
                "recommended_poll_ms": 60000,
                "wait_reason": "error",
                "lines": [
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
