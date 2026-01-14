from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AgentConfig:
    model: str
    reasoning_effort: str
    extra_config: list[str]


@dataclass(frozen=True)
class ExecutionConfig:
    sandbox: str
    approval_policy: str


@dataclass(frozen=True)
class ReadLimits:
    max_files: int
    max_file_bytes: int
    max_total_bytes: int


@dataclass(frozen=True)
class PollingConfig:
    max_ms: int
    jitter_ratio: float


@dataclass(frozen=True)
class RepoConfig:
    execution: ExecutionConfig
    planner: AgentConfig
    coder: AgentConfig
    read_limits: ReadLimits
    polling: PollingConfig


DEFAULTS = RepoConfig(
    execution=ExecutionConfig(sandbox="workspace-write", approval_policy="never"),
    planner=AgentConfig(model="gpt-5.2", reasoning_effort="medium", extra_config=[]),
    coder=AgentConfig(model="gpt-5.1-codex-mini", reasoning_effort="medium", extra_config=[]),
    read_limits=ReadLimits(max_files=30, max_file_bytes=65_536, max_total_bytes=1_000_000),
    polling=PollingConfig(max_ms=60_000, jitter_ratio=0.1),
)


def _get_dict(obj: Any, key: str) -> dict[str, Any]:
    val = obj.get(key) if isinstance(obj, dict) else None
    return val if isinstance(val, dict) else {}


def _get_list_str(obj: dict[str, Any], key: str) -> list[str]:
    val = obj.get(key)
    if isinstance(val, list):
        return [str(x) for x in val if str(x).strip()]
    return []


def merge_config(*, cfg: dict[str, Any] | None, call: dict[str, Any] | None) -> RepoConfig:
    cfg_d = cfg or {}
    call_d = call or {}
    exec_d = _get_dict(cfg_d, "execution") | _get_dict(call_d, "execution")
    planner_d = _get_dict(cfg_d, "planner") | _get_dict(call_d, "planner")
    coder_d = _get_dict(cfg_d, "coder") | _get_dict(call_d, "coder")
    rl_d = _get_dict(cfg_d, "read_limits") | _get_dict(call_d, "read_limits")
    poll_d = _get_dict(cfg_d, "polling") | _get_dict(call_d, "polling")

    def to_int(val: Any, default: int) -> int:
        try:
            return int(val)
        except Exception:
            return default

    sandbox = str(exec_d.get("sandbox") or DEFAULTS.execution.sandbox)
    approval_policy = str(exec_d.get("approval_policy") or DEFAULTS.execution.approval_policy)
    planner_model = str(planner_d.get("model") or DEFAULTS.planner.model)
    planner_reasoning = str(planner_d.get("reasoning_effort") or DEFAULTS.planner.reasoning_effort)
    planner_extra = _get_list_str(planner_d, "extra_config") or list(DEFAULTS.planner.extra_config)
    coder_model = str(coder_d.get("model") or DEFAULTS.coder.model)
    coder_reasoning = str(coder_d.get("reasoning_effort") or DEFAULTS.coder.reasoning_effort)
    coder_extra = _get_list_str(coder_d, "extra_config") or list(DEFAULTS.coder.extra_config)

    max_files = max(1, to_int(rl_d.get("max_files"), DEFAULTS.read_limits.max_files))
    max_file_bytes = max(1, to_int(rl_d.get("max_file_bytes"), DEFAULTS.read_limits.max_file_bytes))
    max_total_bytes = max(1, to_int(rl_d.get("max_total_bytes"), DEFAULTS.read_limits.max_total_bytes))

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
        polling=PollingConfig(max_ms=poll_max_ms, jitter_ratio=poll_jitter),
    )
