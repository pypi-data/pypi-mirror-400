from __future__ import annotations

import argparse

from .config import resolve_config
from .server import build_server


def main() -> None:
    parser = argparse.ArgumentParser(prog="agent-code-squad")
    parser.add_argument("--transport", default="stdio", choices=["stdio"], help="MCP transport")
    parser.add_argument("--dispatch-dir", default=None, help="Override dispatch base directory (default: <repo>/.codex/code-squad)")
    parser.add_argument("--model", default=None, help="Default coder model (env: AGENT_CODE_SQUAD_MODEL)")
    parser.add_argument("--sandbox", default=None, help="Default sandbox (env: AGENT_CODE_SQUAD_SANDBOX)")
    parser.add_argument("--approval-policy", default=None, help="Default approval policy (env: AGENT_CODE_SQUAD_APPROVAL_POLICY)")
    parser.add_argument("--worker-concurrency", type=int, default=None, help="Number of background worker threads (env: AGENT_CODE_SQUAD_WORKER_CONCURRENCY)")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Increase verbosity")
    parser.add_argument("--cwd", default=None, help="Override server startup cwd for repo detection")
    args = parser.parse_args()

    config = resolve_config(
        dispatch_dir=args.dispatch_dir,
        model=args.model,
        sandbox=args.sandbox,
        approval_policy=args.approval_policy,
        verbosity=args.verbose,
        worker_concurrency=args.worker_concurrency,
        cwd=args.cwd,
    )
    server = build_server(config=config)
    server.run(transport=args.transport)
