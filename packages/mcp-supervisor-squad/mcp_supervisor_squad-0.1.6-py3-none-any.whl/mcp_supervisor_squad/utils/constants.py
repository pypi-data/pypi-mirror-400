from __future__ import annotations

BACKOFF_SCHEDULE_MS: tuple[int, ...] = (1000, 2000, 4000, 8000, 15000, 30000, 60000)
MARKER_FILES: tuple[str, ...] = ("package.json", "pyproject.toml", "go.mod", "Cargo.toml")

PHASE_POLL_CAP_MS: dict[str, int] = {
    # Planner/coder tasks can be long-running; allow poll interval to back off to 60s.
    "planner_run": 60_000,
    "coder_run": 60_000,
    "integrate": 30_000,
    "cleanup": 60_000,
}
