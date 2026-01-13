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

1) `code_squad_execute`: start tasks immediately, wait, collect patches, and verify in one call.
2) Optional manual flow:
   - `code_squad_run`: queue tasks and enqueue workers right away.
   - `code_squad_tick`: optional bounded status refresh (enqueues already-queued tasks if needed).
   - `code_squad_status` / `code_squad_events`: poll light status or stream JSONL events.
   - `code_squad_collect`: write patches + touched-files under run artifacts and return them.
   - `code_squad_verify`: run `compileall`/`pytest` or custom `options.commands` arrays; results saved under artifacts.
   - `code_squad_report`: emit run/task summary as `report.json` and `report.md`.
   - `code_squad_prune`: clean up old runs/worktrees by retention policy.
   - `code_squad_cancel` (optional): cancel a job or all tasks in a run.
   - `code_squad_cleanup`: drop worktrees and optionally delete run artifacts.

## Modify Multiple Modules

When the user request is “modify several modules”, prefer one task per module and enforce boundaries so parallel work stays precise.

- Put each module under a distinct directory (example: `modules/<name>/`).
- Use `allow_globs` per task to restrict which files a task is allowed to touch.
- Use `deny_globs` to protect shared areas (configs, app entrypoints, shared libs) from module tasks.
- If scope is violated, `code_squad_execute` returns `status=failed` and writes a scope artifact under `runs/<run_id>/artifacts/scope/<slug>.json`.

Example `code_squad_execute` input:

```json
{
  "cwd": "/path/to/repo",
  "tasks": [
    {
      "name": "user module",
      "scope_name": "modules/user",
      "allow_globs": ["modules/user/**"],
      "deny_globs": ["shared/**", "config/**", "app/**"],
      "prompt": "Fix bug in user module: ... (patch only)"
    },
    {
      "name": "billing module",
      "scope_name": "modules/billing",
      "allow_globs": ["modules/billing/**"],
      "deny_globs": ["shared/**", "config/**", "app/**"],
      "prompt": "Fix bug in billing module: ... (patch only)"
    }
  ],
  "options": {
    "timeout_seconds": 600,
    "poll_interval": 1.0,
    "cleanup": true,
    "keep_failed": true
  }
}
```

## Cleanup and Retention

`code_squad_execute` cleans up worktrees by default to avoid accumulating `.codex/code-squad/worktrees/*`.

- `options.cleanup` (default `true`): remove worktrees after execution
- `options.keep_failed` (default `true`): keep `failed` and `timeout` task worktrees for debugging
- `options.cleanup_delete_run_artifacts` (default `false`): also delete run artifacts (use with care)

For periodic cleanup of old runs/worktrees, use `code_squad_prune`:

- Defaults: keep last `5` runs, keep successful runs for `3` days, keep failed/timeout runs for `1` day
- `dry_run=true` by default; set `dry_run=false` to actually delete

## Logs and Artifacts

Each run writes an index file to make review/debug easier:

- `runs/<run_id>/artifacts/index.json`: run/task summary plus expected artifact paths
- `code_squad_execute` returns `index_path` and writes `index.json` after collect/verify/cleanup
- `code_squad_status` returns `progress` and `next_action`
- `code_squad_events(include_noise=false)` filters out thread/turn/heartbeat noise and command/tool-call items by default

## Tools

- `code_squad_capabilities_get`: defaults and dispatch paths.
- `code_squad_context_pack`: ripgrep-based context pack with snippet/char caps.
- `code_squad_run`: queue tasks with per-task model/sandbox/approval/extra_config (auto-enqueues workers).
- `code_squad_execute`: run -> wait -> collect -> verify in one call.
- `code_squad_tick`: optional bounded worker pump (refresh a few running).
- `code_squad_status`: summarize task states with compact last messages.
- `code_squad_events`: stream compacted JSONL events per job using cursors (supports noise filtering).
- `code_squad_collect`: emit git diffs + touched files per worktree and persist under artifacts.
- `code_squad_verify`: run `compileall`/`pytest` or custom commands using `sys.executable`, persisting results.
- `code_squad_report`: write `report.json`/`report.md` under run artifacts.
- `code_squad_prune`: clean up old runs/worktrees by retention policy.
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
