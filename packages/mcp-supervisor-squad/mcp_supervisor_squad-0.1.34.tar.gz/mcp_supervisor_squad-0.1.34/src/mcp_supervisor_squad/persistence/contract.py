from __future__ import annotations

from pathlib import Path
from typing import Any

from ..planning.config import DEFAULTS, RepoConfig
from .storage import StorageLayout, atomic_write_json, utc_now_iso


CONTRACT_SCHEMA_VERSION = 2


def contract_path_for_repo(layout: StorageLayout) -> Path:
    return layout.base_dir / "contract.json"


def _agent_cfg(agent: Any) -> dict[str, Any]:
    return {
        "model": str(getattr(agent, "model", "")),
        "reasoning_effort": str(getattr(agent, "reasoning_effort", "")),
        "extra_config": list(getattr(agent, "extra_config", []) or []),
    }


def write_repo_contract(*, layout: StorageLayout, cfg: RepoConfig, package_version: str) -> Path:
    """
    Write a machine-readable contract describing current behavior, limits, and file locations.

    This is the authoritative reference for external supervisors, to avoid relying on stale AGENTS.md.
    """
    payload: dict[str, Any] = {
        "contract_schema_version": CONTRACT_SCHEMA_VERSION,
        "package": {"name": "mcp-supervisor-squad", "version": str(package_version or "")},
        "generated_at": utc_now_iso(),
        "principles": {
            "external_output": "squad_status returns summary+events lines+forced_wait_ms; details are persisted under .codex/supervisor-squad/",
            "max_project_roots": 2,
            "no_compat": True,
        },
        "paths": {
            "base_dir": str(layout.base_dir),
            "runs_dir": str(layout.runs_dir),
            "kb_dir": str(layout.kb_dir),
            "worktrees_dir": str(layout.worktrees_dir),
            "repo_contract": str(contract_path_for_repo(layout)),
            "kb_repo_profile": str(layout.kb_dir / "repo_profile.json"),
            "kb_compact": str(layout.kb_dir / "compact.md"),
            "kb_inbox_md": str(layout.kb_dir / "inbox" / "director_report.md"),
            "kb_inbox_json": str(layout.kb_dir / "inbox" / "director_report.json"),
            "kb_archive_dir": str(layout.kb_dir / "archive"),
        },
        "limits": {
            "director_report_max_kb": int(cfg.kb.inbox_max_kb),
            "compact_max_kb": int(cfg.kb.compact_max_kb),
            "archive_keep": int(cfg.kb.archive_keep),
            "archive_max_kb": int(cfg.kb.archive_max_kb),
            "read_limits": {
                "max_files": int(cfg.read_limits.max_files),
                "max_file_bytes": int(cfg.read_limits.max_file_bytes),
                "max_total_bytes": int(cfg.read_limits.max_total_bytes),
            },
            "contract_json_max_bytes": 4096,
        },
        "config": {
            "config_path": str(layout.base_dir / "config.json"),
            "defaults": {
                "execution": {
                    "sandbox": DEFAULTS.execution.sandbox,
                    "approval_policy": DEFAULTS.execution.approval_policy,
                },
                "planner": _agent_cfg(DEFAULTS.planner),
                "coder": _agent_cfg(DEFAULTS.coder),
                "read_limits": {
                    "max_files": DEFAULTS.read_limits.max_files,
                    "max_file_bytes": DEFAULTS.read_limits.max_file_bytes,
                    "max_total_bytes": DEFAULTS.read_limits.max_total_bytes,
                },
                "kb": {
                    "inbox_max_kb": DEFAULTS.kb.inbox_max_kb,
                    "compact_max_kb": DEFAULTS.kb.compact_max_kb,
                    "archive_keep": DEFAULTS.kb.archive_keep,
                    "archive_max_kb": DEFAULTS.kb.archive_max_kb,
                },
                "polling": {
                    "max_ms": DEFAULTS.polling.max_ms,
                    "jitter_ratio": DEFAULTS.polling.jitter_ratio,
                },
            },
            "effective": {
                "execution": {"sandbox": cfg.execution.sandbox, "approval_policy": cfg.execution.approval_policy},
                "planner": _agent_cfg(cfg.planner),
                "coder": _agent_cfg(cfg.coder),
                "read_limits": {
                    "max_files": cfg.read_limits.max_files,
                    "max_file_bytes": cfg.read_limits.max_file_bytes,
                    "max_total_bytes": cfg.read_limits.max_total_bytes,
                },
                "kb": {
                    "inbox_max_kb": cfg.kb.inbox_max_kb,
                    "compact_max_kb": cfg.kb.compact_max_kb,
                    "archive_keep": cfg.kb.archive_keep,
                    "archive_max_kb": cfg.kb.archive_max_kb,
                },
                "polling": {"max_ms": cfg.polling.max_ms, "jitter_ratio": cfg.polling.jitter_ratio},
            },
        },
        "workflow": {
            "tools": ["squad_start", "squad_status", "squad_apply"],
            "recommended_call_chain": ["squad_start", "poll squad_status", "squad_apply(dry_run=true)", "squad_apply(dry_run=false)"],
            "phases": ["planner_light", "planner_heavy", "coder_run", "integrate", "done", "cleanup", "error"],
            "required_parameters": {
                "squad_status": {"options.cwd": "absolute path inside the target repo"},
                "squad_apply": {"options.cwd": "absolute path inside the target repo", "options.dry_run": "bool (default true)"},
            },
            "notes": [
                "Always pass options.cwd (absolute path) for squad_status/squad_apply; do not pass CLI-style strings.",
                "To inject director input, write kb/inbox/director_report.md|json before calling squad_start.",
                "After squad_start, inbox is archived and cleared; compact.md is updated for reuse.",
                "squad_status returns summary_lines/event_lines/forced_wait_ms (no has_update/event_id); if event_lines empty, only summary_lines contains 等待提示 + forced_wait_ms.",
                "Force print: whenever squad_start/squad_status returns summary_lines/event_lines, print them line by line in the current conversation (keep concise).",
                "When phase is done/canceled/error, forced_wait_ms=0 and clients should stop polling squad_status.",
                "Planner is two-phase: light scan for quick summary, then heavy scan to produce requirements (plan_scan -> exec_scan -> write_requirements). Evidence is tool-executed, not LLM-invented.",
                "If you detect a wrong plan, cancel with squad_status options={cwd, cancel:true} then start a new run.",
            ],
        },
    }
    path = contract_path_for_repo(layout)
    atomic_write_json(path, payload)
    return path
