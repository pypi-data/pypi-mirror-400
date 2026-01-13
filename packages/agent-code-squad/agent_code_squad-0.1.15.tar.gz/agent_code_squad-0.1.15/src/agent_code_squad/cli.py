from __future__ import annotations

import argparse

from .config import resolve_config
from .server import build_server


def main() -> None:
    parser = argparse.ArgumentParser(prog="agent-code-squad")
    parser.add_argument("--dispatch-dir", default=None, help="Override dispatch base directory (fallback when code-squad/config.json has no dispatch_dir)")
    parser.add_argument("--model", default=None, help="Default coder model (fallback when code-squad/config.json has no defaults.model)")
    parser.add_argument("--sandbox", default=None, help="Default sandbox (fallback when code-squad/config.json has no defaults.sandbox)")
    parser.add_argument("--approval-policy", default=None, help="Default approval policy (fallback when code-squad/config.json has no defaults.approval_policy)")
    parser.add_argument("--worker-concurrency", type=int, default=None, help="Number of background worker threads (fallback when code-squad/config.json has no defaults.worker_concurrency)")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Increase verbosity")
    parser.add_argument("--cwd", default=None, help="Override server startup cwd for repo detection")
    args = parser.parse_args()

    config = resolve_config(
        dispatch_dir=args.dispatch_dir,
        model=args.model,
        sandbox=args.sandbox,
        approval_policy=args.approval_policy,
        verbosity=args.verbose if args.verbose else None,
        worker_concurrency=args.worker_concurrency,
        cwd=args.cwd,
    )
    server = build_server(config=config)
    server.run(transport="stdio")
