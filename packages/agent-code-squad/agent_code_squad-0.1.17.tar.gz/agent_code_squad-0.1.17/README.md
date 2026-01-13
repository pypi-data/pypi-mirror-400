# agent-code-squad

Python MCP server that queues code-writing subagents with minimal context packs, isolated git worktrees, and patch-first collection. Heavy work (git worktree add + codex exec start) runs in a background worker to avoid tool-call timeouts.

## Quickstart

```sh
cd mcp-tools/agent-code-squad
poetry env use python3
poetry install
poetry run agent-code-squad
```

## MCP client config (example)

```toml
[mcp_servers.agent-code-squad]
command = "poetry"
args = ["run", "agent-code-squad"]
cwd = "/Volumes/workspace/dzrlab/k3s-test/mcp-tools/agent-code-squad"
```

## Project config (recommended)

Create `<repo_root>/.codex/code-squad/config.json` to set defaults per project.

Priority: `.codex/code-squad/config.json` → CLI flags → built-in defaults.

Example:

```json
{
  "dispatch_dir": "~/.codex/code-squad",
  "defaults": {
    "model": "gpt-5.2-codex",
    "sandbox": "workspace-write",
    "approval_policy": "never",
    "auto_context_pack": {
      "enabled": true,
      "glob": "**/*",
      "max_files": 14,
      "max_snippets": 28,
      "max_total_chars": 24000,
      "hints": []
    },
    "worker_concurrency": 2
  },
  "guardrails": {
    "enforce_sparse_checkout": true,
    "early_scope_enforcement": true,
    "strict_context_pack_scope": true,
    "require_patch": true
  },
  "energy_saver": {
    "default_reasoning_effort": "medium",
    "max_reasoning_effort": "medium"
  }
}
```

## Recommended flow

1) `code_squad_execute`: start tasks immediately and return quickly (default non-blocking).
2) Optional manual flow:
   - `code_squad_run`: queue tasks and enqueue workers right away.
   - `code_squad_tick`: optional bounded status refresh (enqueues already-queued tasks if needed).
   - `code_squad_status` / `code_squad_events`: poll light status heartbeats or aggregated phase summaries (see Status & Events).
   - `code_squad_collect`: extract patches from job stdout and persist under run artifacts (works even after worktree cleanup).
   - `code_squad_verify`: optional; runs `compileall`/`pytest` or custom `options.commands` arrays; results saved under artifacts.
   - `code_squad_report`: emit run/task summary as `report.json` and `report.md`.
   - `code_squad_prune`: clean up old runs/worktrees by retention policy.
   - `code_squad_cancel` (optional): cancel a job or all tasks in a run.
   - `code_squad_cleanup`: drop worktrees and optionally delete run artifacts.

## Default preflight (code_squad_execute)

- Phase A runs automatically before execution (set `options.preflight=false` to skip):
  - Scope preview: validates `allow_globs`/`deny_globs` and samples files (uses `rg`; missing rg triggers a confirmation question).
  - Context budget check: flags very high `auto_context_pack.max_total_chars`, overly broad hints, or disabled context packs when they are required for the selected execution mode.
  - Task-count sanity: warns when a run contains a very large number of tasks or obvious over-splitting; set `options.preflight_allow_many_tasks=true` to opt out when intentionally queuing many fine-grained tasks.
  - Prompt rules: ensures prompts include patch-only, acceptance/verification, and “ask if missing info” instructions.
- Decision logic:
  - High-confidence pass → auto enqueue/run (preflight summary is included in the response and run artifacts).
  - Gaps (wide/empty scope, oversized context, missing prompt rules) → return `preflight.needs_user_confirm=true`, `next_action=confirm`, no tasks started.
- Artifacts: preflight summary is stored under `runs/<run_id>/artifacts/docs/preflight.md` and embedded in `artifacts.preflight_doc` + the `preflight` block in responses/index JSON.

## Modify Multiple Modules

When the user request is “modify several modules”, prefer one task per module and enforce boundaries so parallel work stays precise.

- Put each module under a distinct directory (example: `modules/<name>/`).
- Use `allow_globs` per task to restrict which files a task is allowed to touch.
- Use `deny_globs` to protect shared areas (configs, app entrypoints, shared libs) from module tasks.
- `allow_globs` / `deny_globs` are also injected into the subagent prompt as hard rules to reduce scope drift.
- If `allow_globs` is set, the worktree attempts a best-effort `git sparse-checkout` to physically hide non-allowed paths (further reducing context + accidental edits). The mapping prefers the tightest directory prefix (e.g. `modules/user/**` → `modules/user`).
- If scope is violated, collection marks `scope.ok=false` and writes a scope artifact under `runs/<run_id>/artifacts/scope/<slug>.json`.

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
    "poll_interval": 1.0,
    "wait_seconds": 0,
    "cleanup": true,
    "keep_failed": true
  }
}
```

## Multi-Agent Pipeline (roles + depends_on)

- Optional per-task `role` (planner/coder/reviewer/integrator) and `depends_on` lists enable staged pipelines.
- Tasks enqueue only after all dependencies finish with `state=completed`; failed/cancelled/timeout deps mark dependents as `blocked` (terminal).
- `code_squad_status` / `code_squad_tick` / background finalizer auto-check dependencies and enqueue ready tasks—no manual requeue needed.
- Use `code_squad_apply_many` to integrate multiple patches in order (default dry-run, stop on first error). Flags: `options.dry_run` (default `true`), `options.stop_on_error` (default `true`), `options.three_way` (default `true`), `options.stage_index` (default `true`).
- Downstream reviewers/integrators can set `include_dep_patches=true` to stream dependency diffs into their prompt; cap payloads with `dep_patch_max_bytes` (per-task override) when upstream coders touch large surfaces.

Example:

```json
{
  "tasks": [
    {
      "name": "plan",
      "role": "planner",
      "prompt": "Decompose feature X into sub-tasks for api/ui/docs.",
      "allow_globs": ["docs/**"]
    },
    {
      "name": "api fix",
      "role": "coder",
      "depends_on": ["plan"],
      "prompt": "Apply planner decisions to API layer",
      "allow_globs": ["apps/api-fastapi/**"],
      "deny_globs": ["**/node_modules/**", "**/.codex/**"]
    },
    {
      "name": "ui polish",
      "role": "coder",
      "depends_on": ["plan"],
      "prompt": "Apply planner decisions to UI layer",
      "allow_globs": ["apps/ui/**"],
      "deny_globs": ["**/node_modules/**", "**/.codex/**"]
    },
    {
      "name": "review",
      "role": "reviewer",
      "depends_on": ["api fix", "ui polish"],
      "prompt": "Review diffs from api/ui tasks and propose risk notes",
      "allow_globs": ["apps/api-fastapi/**", "apps/ui/**", "docs/**"]
    }
  ]
}
```

After `collect`, run a batch integration dry-run:

```json
code_squad_apply_many(
  cwd="/path/to/repo",
  run_id="<run>",
  slugs=["api-fix", "ui-polish"],
  options={"dry_run": true, "stop_on_error": true}
)
```

Reviewer/integrator example that ingests upstream coder patches:

```json
{
  "tasks": [
    {
      "name": "api review",
      "role": "reviewer",
      "depends_on": ["api fix"],
      "include_dep_patches": true,
      "dep_patch_max_bytes": 20000,
      "prompt": "Inspect API diffs and leave inline feedback (patch only).",
      "allow_globs": ["apps/api-fastapi/**", "docs/**"]
    },
    {
      "name": "integrate",
      "role": "integrator",
      "depends_on": ["api review", "ui polish"],
      "include_dep_patches": true,
      "dep_patch_max_bytes": 16000,
      "prompt": "Merge reviewed patches, resolve conflicts, and prep final diff (patch only).",
      "allow_globs": ["apps/api-fastapi/**", "apps/ui/**"]
    }
  ]
}
```

## Status & Events

- `options.status_verbosity` (default `brief`) controls surface area:
  - `brief`: 1–2 line heartbeat with no internal IDs. Line one must summarize the current phase/step, progress, pending confirmations, and any failure reason/action, e.g.
    - `进度: 2/5 | 正在: tools-status-preflight-cleanup | 动作: 生成补丁`
    - `最近进展: 完成 scope 校验；已生成 patch（15KB）；等待 collect/apply`
    - Only when the state changes or user action is required, append one extra line such as `需要确认: preflight 检测到 tasks 过多（12 > 6），建议合并；如确认继续：options.preflight_allow_many_tasks=true`.
  - `normal`: same heartbeat plus compact per-task state (queued/running/completed/failed) without exposing IDs.
  - `debug`: adds raw troubleshooting details (job_id, counts, cursor, run paths, raw events).
- Internal identifiers (`run_id`, `task_slug`, `job_id`, `pid`, `cursor`) remain required internally but are hidden unless `options.status_verbosity=debug`.
- `code_squad_events` defaults to phase summaries rather than raw JSONL streams. Phases: `preflight`, `context_pack`, `worktree`, `agent_run`, `collect`, `cleanup`. Use `options.debug=true` or `include_noise=true` for raw job events.

## Execution Modes

`options.execution_mode` selects how tasks run (defaults to the fastest safe choice determined during preflight):

- `direct`: single agent runs inside the current repo without creating a worktree. Best for ≤2 tasks touching ≤3 files (docs and surgical fixes). Fastest, but enforces low-risk scope.
- `batch-worktree`: creates one worktree to process a batch of related tasks sequentially within the same agent. Avoids spawning N worktrees while isolating from the main tree.
- `fanout`: current behavior—each task gets its own worktree and may run in parallel.

Preflight heuristics:

- `tasks<=2` and estimated `touched_files<=3` → `direct`.
- Too many tasks or overlapping scopes → `batch-worktree` (preflight strongly suggests merging before continuing).
- Disjoint independent scopes → `fanout`.

## Auto Context Packs (Default)

Automatic context packs are cached under `<dispatch_base>/context_packs/`, but load shedding is applied based on execution mode:

- `direct` / `batch-worktree`: `options.auto_context_pack` defaults to disabled (or capped at ~8–12k chars). Enable explicitly only when the scope is unclear or cross-file reasoning is required. `batch-worktree` tasks share one generated pack.
- `fanout`: packs stay enabled and cached; tasks with the same prefix reuse packs across worktrees.
- Override caps via `options.auto_context_pack` (dict keys `glob`, `max_files`, `max_snippets`, `max_total_chars`, optional `hints`).
- Query selection per task: `task.context_query` → `task.scope_name` → `task.name`.
- `allow_globs` / `deny_globs` filters apply to snippet selection to reduce leakage, and the pack still seeds core entrypoints (`AGENTS.md`, `README*`, build metadata) before ripgrep extraction.

## Change Size Limits (Optional)

To prevent large/low-signal edits:

- Per-task: `task.max_touched_files`, `task.max_patch_bytes`
- Or defaults: `options.max_touched_files`, `options.max_patch_bytes`

If limits are exceeded, scope is marked `ok=false` and `code_squad_execute` fails the task.

## Scope Guardrails (Hardening)

- `enforce_sparse_checkout` (default `true`): if `allow_globs` is set, sparse-checkout runs before the subagent starts; failures hard-fail the task.
- `early_scope_enforcement` (default `true`): once a patch appears in stdout, scope is checked immediately; violations cancel the job early.
- `strict_context_pack_scope` (default `true`): provided `task.context_pack` is rejected if it contains out-of-scope paths (based on `allow_globs`/`deny_globs`).
- `require_patch` (default `true`): tasks that finish without a patch are treated as failed (scope `limits.require_patch`).

## Cleanup and Retention

Cleanup remains automatic so brief status updates do not spam internals. Expect a single completion note such as `已清理临时目录`; debug verbosity lists specific worktrees and prune output. When `options.keep_failed=true`, brief status calls out that failed/timeout worktrees remain for inspection until `code_squad_cleanup` or `code_squad_prune` is invoked.

Worktree cleanup is controlled by `options.cleanup` / `options.keep_failed` (used by the background finalizer).

- `options.cleanup` (default `true`): remove worktrees after execution.
- `options.keep_failed` (default `true`): keep `failed` and `timeout` task worktrees for debugging.
- `options.cleanup_delete_run_artifacts` (default `false`): also delete run artifacts (use with care).

The finalizer runs `git worktree prune` after each cleanup pass and removes empty `.codex/code-squad/worktrees/<run_id>` directories so stale run folders do not accumulate. Use `code_squad_cleanup` when you need to immediately drop worktrees for a specific run (and optionally its artifacts) without waiting for the automatic finalizer window.

For periodic cleanup of old runs/worktrees, use `code_squad_prune`:

- Defaults: keep last `5` runs, keep successful runs for `3` days, keep failed/timeout runs for `1` day.
- `dry_run=true` by default; set `dry_run=false` to actually delete.

## Logs and Artifacts

Each run writes an index file to make review/debug easier:

- `runs/<run_id>/artifacts/index.json`: run/task summary plus expected artifact paths.
- `code_squad_execute` returns quickly with `index_path` and `next_poll_ms`; heavy work is done asynchronously.
- `runs/<run_id>/artifacts/timeline.jsonl`: structured timeline events (used by `recent_events` in status/execute/collect).
- `code_squad_status` returns the heartbeat described in Status & Events, including `progress`, `next_action`, `next_poll_ms`, per-task status when verbosity ≥ `normal`, and `has_patch`.
- `code_squad_events` aggregates by phase (`preflight`, `context_pack`, `worktree`, `agent_run`, `collect`, `cleanup`) instead of streaming raw JSONL; set `include_noise=true` or `options.debug=true` to stream the raw job events.
- `code_squad_collect` persists patches to disk and returns paths by default; set `options.include_patch=true` to inline patch text in the response.

## Reasoning effort cap (eco)

This server enforces `model_reasoning_effort<=max_reasoning_effort` for all tasks (default max is `medium`).

- If you want lower effort, set `options.model_reasoning_effort="low"` (or `options.reasoning_effort="low"`).
- Requests above the configured max are clamped down to the max.

## Tools

- `code_squad_capabilities_get`: defaults and dispatch paths.
- `code_squad_capabilities_get` supports `cwd` to resolve per-repo defaults from `<repo_root>/.codex/code-squad/config.json` (useful when the MCP server is started globally without a fixed cwd).
- `code_squad_scope_preview`: preview allow/deny globs before running tasks.
- `code_squad_context_pack`: ripgrep-based context pack with snippet/char caps.
- `code_squad_run`: queue tasks with per-task model/sandbox/approval/extra_config (auto-enqueues workers).
- `code_squad_execute`: start run and return quickly (optional short wait via `options.wait_seconds`).
- `code_squad_tick`: optional bounded worker pump (refresh a few running).
- `code_squad_status`: summarize progress as a heartbeat (controlled by `options.status_verbosity=brief|normal|debug`).
- `code_squad_events`: return aggregated phase summaries by default (raw JSONL + cursors only in debug / `include_noise=true`).
- `code_squad_collect`: extract patch + touched files from job stdout and persist under artifacts.
- `code_squad_apply`: apply a collected patch to the repo worktree (default dry-run; supports `--3way` + `--index`).
- `code_squad_apply_many`: apply multiple collected patches in order (default dry-run, stop on first error).
- `code_squad_verify`: run `compileall`/`pytest` or custom commands using `sys.executable`, persisting results.
- `code_squad_report`: write `report.json`/`report.md` under run artifacts.
- `code_squad_prune`: clean up old runs/worktrees by retention policy.
- `code_squad_cancel`: cancel a job or whole run (sets state to `cancelled`).
- `code_squad_cleanup`: remove worktrees and (optional) run artifacts under `.codex/code-squad/`.

## Debug output

All tools accept `options.debug=true` to return a `debug` block (paths, timings, raw stdout/stderr/events). Default responses stay minimal and omit worktree/run/dispatch paths, trace IDs, PIDs, and full prompts.

For robustness, `options` is treated as best-effort: non-dict inputs are coerced to `{}` rather than hard-failing validation.

## Paths and defaults

- Run metadata: `<dispatch_base>/runs/<run_id>/run.json`.
- Job artifacts: `<dispatch_base>/runs/<run_id>/jobs/<job_id>/{meta.json,stdout.jsonl,stderr.log,last_message.txt}`.
- Worktrees: `<repo>/.codex/code-squad/worktrees/<run_id>/<task_slug>`.
- Dispatch base (default): `<repo>/.codex/code-squad`.
- Defaults: model `gpt-5.1-codex-max`, sandbox `workspace-write`, approval policy `never`, worker concurrency `2`.
- Override via `.codex/code-squad/config.json` or CLI flags (config takes priority over CLI).
