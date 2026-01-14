from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..persistence.storage import read_json


def _get_dict(obj: Any, key: str) -> dict[str, Any]:
    if not isinstance(obj, dict):
        return {}
    val = obj.get(key)
    return val if isinstance(val, dict) else {}


def _get_list_str(obj: Any, key: str) -> list[str]:
    if not isinstance(obj, dict):
        return []
    val = obj.get(key)
    if not isinstance(val, list):
        return []
    return [str(x) for x in val if str(x).strip()]


@dataclass(frozen=True, slots=True)
class AgentConfig:
    model: str
    reasoning_effort: str
    extra_config: list[str]


@dataclass(frozen=True, slots=True)
class ReadLimits:
    max_files: int
    max_file_bytes: int
    max_total_bytes: int


@dataclass(frozen=True, slots=True)
class KBConfig:
    inbox_max_kb: int
    compact_max_kb: int
    archive_keep: int
    archive_max_kb: int


@dataclass(frozen=True, slots=True)
class PollingConfig:
    max_ms: int
    jitter_ratio: float


@dataclass(frozen=True, slots=True)
class ExecutionConfig:
    sandbox: str
    approval_policy: str


@dataclass(frozen=True, slots=True)
class RepoConfig:
    execution: ExecutionConfig
    planner: AgentConfig
    coder: AgentConfig
    read_limits: ReadLimits
    kb: KBConfig
    polling: PollingConfig


DEFAULTS = RepoConfig(
    execution=ExecutionConfig(sandbox="workspace-write", approval_policy="never"),
    planner=AgentConfig(model="gpt-5.2", reasoning_effort="medium", extra_config=[]),
    coder=AgentConfig(model="gpt-5.1-codex-max", reasoning_effort="medium", extra_config=[]),
    read_limits=ReadLimits(max_files=30, max_file_bytes=65_536, max_total_bytes=1_000_000),
    kb=KBConfig(inbox_max_kb=20, compact_max_kb=10, archive_keep=5, archive_max_kb=200),
    polling=PollingConfig(max_ms=60_000, jitter_ratio=0.1),
)


def load_repo_config(repo_root: Path) -> dict[str, Any]:
    path = repo_root / ".codex" / "supervisor-squad" / "config.json"
    raw = read_json(path)
    return raw if isinstance(raw, dict) else {}


def effective_config(*, repo_root: Path, options: dict[str, Any]) -> RepoConfig:
    """
    Merge precedence: defaults < repo config.json < call options.

    Schema:
    - execution: { sandbox, approval_policy }
    - planner: { model, reasoning_effort, extra_config: [] }
    - coder: { model, reasoning_effort, extra_config: [] }
    - read_limits: { max_files, max_file_bytes, max_total_bytes }
    - kb: { inbox_max_kb, compact_max_kb, archive_keep, archive_max_kb }
    - polling: { max_ms, jitter_ratio }
    """
    cfg = load_repo_config(repo_root)
    call = options if isinstance(options, dict) else {}

    def merged(src_a: dict[str, Any], src_b: dict[str, Any]) -> dict[str, Any]:
        out = dict(src_a)
        out.update(src_b)
        return out

    exec_d = merged(_get_dict(cfg, "execution"), _get_dict(call, "execution"))
    pln_d = merged(_get_dict(cfg, "planner"), _get_dict(call, "planner"))
    cod_d = merged(_get_dict(cfg, "coder"), _get_dict(call, "coder"))
    rl_d = merged(_get_dict(cfg, "read_limits"), _get_dict(call, "read_limits"))
    kb_d = merged(_get_dict(cfg, "kb"), _get_dict(call, "kb"))
    poll_d = merged(_get_dict(cfg, "polling"), _get_dict(call, "polling"))

    sandbox = str(exec_d.get("sandbox") or DEFAULTS.execution.sandbox)
    approval_policy = str(exec_d.get("approval_policy") or DEFAULTS.execution.approval_policy)

    planner_model = str(pln_d.get("model") or DEFAULTS.planner.model)
    planner_reasoning = str(pln_d.get("reasoning_effort") or DEFAULTS.planner.reasoning_effort)
    planner_extra = _get_list_str(pln_d, "extra_config") or list(DEFAULTS.planner.extra_config)

    coder_model = str(cod_d.get("model") or DEFAULTS.coder.model)
    coder_reasoning = str(cod_d.get("reasoning_effort") or DEFAULTS.coder.reasoning_effort)
    coder_extra = _get_list_str(cod_d, "extra_config") or list(DEFAULTS.coder.extra_config)

    def to_int(val: Any, default: int) -> int:
        try:
            return int(val)
        except Exception:
            return default

    max_files = max(1, to_int(rl_d.get("max_files"), DEFAULTS.read_limits.max_files))
    max_file_bytes = max(1, to_int(rl_d.get("max_file_bytes"), DEFAULTS.read_limits.max_file_bytes))
    max_total_bytes = max(1, to_int(rl_d.get("max_total_bytes"), DEFAULTS.read_limits.max_total_bytes))

    inbox_max_kb = max(1, to_int(kb_d.get("inbox_max_kb"), DEFAULTS.kb.inbox_max_kb))
    compact_max_kb = max(1, to_int(kb_d.get("compact_max_kb"), DEFAULTS.kb.compact_max_kb))
    archive_keep = max(0, to_int(kb_d.get("archive_keep"), DEFAULTS.kb.archive_keep))
    archive_max_kb = max(1, to_int(kb_d.get("archive_max_kb"), DEFAULTS.kb.archive_max_kb))

    poll_max_ms = max(5_000, to_int(poll_d.get("max_ms"), DEFAULTS.polling.max_ms))
    try:
        poll_jitter = float(poll_d.get("jitter_ratio") if "jitter_ratio" in poll_d else DEFAULTS.polling.jitter_ratio)
    except Exception:
        poll_jitter = DEFAULTS.polling.jitter_ratio
    poll_jitter = max(0.0, min(0.5, poll_jitter))

    return RepoConfig(
        execution=ExecutionConfig(sandbox=sandbox, approval_policy=approval_policy),
        planner=AgentConfig(model=planner_model, reasoning_effort=planner_reasoning, extra_config=planner_extra),
        coder=AgentConfig(model=coder_model, reasoning_effort=coder_reasoning, extra_config=coder_extra),
        read_limits=ReadLimits(max_files=max_files, max_file_bytes=max_file_bytes, max_total_bytes=max_total_bytes),
        kb=KBConfig(
            inbox_max_kb=inbox_max_kb,
            compact_max_kb=compact_max_kb,
            archive_keep=archive_keep,
            archive_max_kb=archive_max_kb,
        ),
        polling=PollingConfig(max_ms=poll_max_ms, jitter_ratio=poll_jitter),
    )
