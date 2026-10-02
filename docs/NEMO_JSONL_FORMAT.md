# NeMo rollout JSONL — `sites` / `start_urls` contract

*Changed 2026-08-22. Applies to every `webarena_*_batch_*.jsonl` emitted by
`scripts/export_nemo_rollouts.py`.*

## The contract

```jsonc
"sites":      ["webarena_gitlab_mock"],
"start_urls": ["/byteblaze/empathy-prompts/-/settings/ci_cd"]
```

- `sites` — one entry per app the task touches, in `task.json` `apps` order.
- `start_urls` — **strictly parallel to `sites`**; `start_urls[i]` is the start
  location for `sites[i]`. Always the same length as `sites`.
- Each entry is the `start_path` the task was authored and verified against, or
  the **empty string** `""` when that app starts at its default location.
- Entries are **paths, not absolute URLs**. The base differs per deployment and is
  resolved from the endpoint registry / `CUA_GYM_WEBARENA_*_URL` at episode time.

`task.json` is authoritative. If a bundle's `nemo_task.json` carries a `sites`
value that disagrees, the exporter uses `task.json` and reports it as a problem —
`task.json` is what the verification harness actually navigated to.

## How to join a start URL

```
<base><start_path>?sid=<sid>
```

The path must come **before** the query. `?sid=<sid><start_path>` is wrong: `?`
terminates the path component, so the whole trailing path becomes part of the sid
*value* and the router only ever sees `/`.

This is easy to get wrong because **the broken form does not error**. The mocks are
SPAs, so any path returns the app shell with HTTP 200 and an unknown sid is just a
new session. Verify by page identity, not status code:

| URL | renders |
|---|---|
| `…:8001/byteblaze/empathy-prompts/-/settings/ci_cd?sid=X` | `CI/CD Settings · …` |
| `…:8001/?sid=X/byteblaze/empathy-prompts/-/settings/ci_cd` | `Projects · Dashboard` (wrong) |
| `…:8001/?sid=X` | `Projects · Dashboard` (default start) |

Why: `main.jsx` mounts a `BrowserRouter` and `App.jsx:169` reads
`const { pathname, search } = useLocation()`. The route is matched on `pathname`;
the sid is read from `search`. Two different components of the URL.

## Why this changed

Before this change the exporter never wrote `start_urls` — 995 of 997 rows across
the three batches had `[]`, and no start path appeared anywhere in the row.

That mattered because the two runtimes disagree:

- `cua_gym_web/runner.py:277` composes `endpoints[source].base_url + app.start_path`
  and calls `with_sid()`. **This is the harness that verified every task**, so a
  passing `initial 0.0 -> replay 1.0` was recorded from the deep link.
- `cuagym/browser_worker.py:195` hardcodes `start_url = f"{base_url}/?sid={sid}"`
  and never reads `start_urls` at all.

So tasks verified from a deep link were being rolled out from the app root.
**596 of 600** batch-3 tasks declare a non-default `start_path`.

Populating `start_urls` is necessary but **not sufficient**: `cuagym` still ignores
the field. Until `browser_worker.py` is changed to honour it, NeMo rollouts continue
to start at the root regardless of what the row says.

## What a passing verification does and does not tell you

A task verified at `initial 0.0 -> replay 1.0` is well-formed and its reward
discriminates. It does **not** establish that the task is solvable from the app
root, which is a separate property. For the GitLab settings family it currently is
not, by clicking: `routeContext.js:126` classifies section `edit` as
`['repository','files']`, while the sidebar's own Settings link points at
`/:ns/:proj/edit` (`ProjectSidebar.jsx:111`) and submenus render only when their
top-level item is active (`ProjectSidebar.jsx:172`). Landing on Settings General
therefore collapses the Settings submenu, so its seven sub-pages have no click
path. `Breadcrumbs.jsx:133` disambiguates the same case correctly with
`ctx.section === 'edit' && !ctx.infix`; `projectSidebarActive` ignores `ctx.infix`.
Unfixed as of this writing — `hub/` is out of scope for edits.
