"""CLI entry point for the MCP server."""

from __future__ import annotations

import argparse

from .server import run_server
from . import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the mcp-supervisor-squad MCP server.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--transport",
        default="stdio",
        choices=["stdio"],
        help="Transport to use for the MCP server.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    run_server(transport=args.transport)
