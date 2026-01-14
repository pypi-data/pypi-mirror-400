BACKOFF_SCHEDULE_MS = [4000, 6000, 8000, 10000, 12000, 15000]
PHASE_POLL_CAP_MS = {
    "coder_run": 10000,
    "done": 0,
    "error": 0,
    "canceled": 0,
}
MARKER_FILES = {".git", "package.json", "pnpm-workspace.yaml", "pyproject.toml"}
