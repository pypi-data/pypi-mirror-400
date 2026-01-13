# agent-code-squad

Python MCP server that queues code-writing subagents with minimal context packs, isolated git worktrees, and patch-first collection. Heavy work (git worktree add + codex exec start) runs in a background worker to avoid tool-call timeouts.

## Quickstart

```sh
cd mcp-tools/agent-code-squad
poetry env use python3
poetry install
poetry run agent-code-squad --transport stdio
```

## MCP client config (example)

```toml
[mcp_servers.agent-code-squad]
command = "poetry"
args = ["run", "agent-code-squad", "--transport", "stdio"]
cwd = "/Volumes/workspace/dzrlab/k3s-test/mcp-tools/agent-code-squad"
```

## Recommended flow

1) `code_squad_run`: enqueue tasks (no worktree/git/codex start yet).
2) `code_squad_tick`: start a few queued tasks via the background worker and refresh running statuses.
3) `code_squad_status` / `code_squad_events`: poll light status or stream JSONL events.
4) `code_squad_collect`: grab git diffs from task worktrees (works even while jobs run).
5) `code_squad_verify`: run `compileall` and optional `pytest` inside a worktree.
6) `code_squad_cancel` (optional): cancel a job or all tasks in a run.
7) `code_squad_cleanup`: drop worktrees and optionally delete run artifacts.

## Tools

- `code_squad_capabilities_get`: defaults and dispatch paths.
- `code_squad_context_pack`: ripgrep-based context pack with snippet/char caps.
- `code_squad_run`: queue tasks with per-task model/sandbox/approval/extra_config.
- `code_squad_tick`: bounded worker pump (start queued tasks, refresh a few running).
- `code_squad_status`: summarize task states with compact last messages.
- `code_squad_events`: stream compacted JSONL events per job using cursors.
- `code_squad_collect`: emit git diffs + touched files per worktree.
- `code_squad_verify`: run `compileall` and optional `pytest` using `sys.executable`.
- `code_squad_cancel`: cancel a job or whole run (sets state to `cancelled`).
- `code_squad_cleanup`: remove worktrees and (optional) run artifacts under `.codex/code-squad/`.

## Debug output

All tools accept `options.debug=true` to return a `debug` block (paths, timings, raw stdout/stderr/events). Default responses stay minimal and omit worktree/run/dispatch paths, trace IDs, PIDs, and full prompts.

## Paths and defaults

- Run metadata: `<dispatch_base>/runs/<run_id>/run.json`.
- Job artifacts: `<dispatch_base>/runs/<run_id>/jobs/<job_id>/{meta.json,stdout.jsonl,stderr.log,last_message.txt}`.
- Worktrees: `<repo>/.codex/code-squad/worktrees/<run_id>/<task_slug>`.
- Dispatch base (default): `<repo>/.codex/code-squad`.
- Defaults: model `gpt-5.1-codex-max`, sandbox `workspace-write`, approval policy `never`. Override via CLI flags or `AGENT_CODE_SQUAD_*` env vars.
