# SETUP.md — bootstrapping a new machine to run TASK.md

TASK.md assumes an environment that a `git clone` does **not** reproduce. Five of
its dependencies live outside the repository, and one statement in it is stale.
Work through this file first; TASK.md's Phase 1 preflight then becomes a check
rather than a setup step.

Everything here was verified against a working deployment on 2026-10-02.

---

## 0. What the clone is missing, in one table

| Thing | Why a clone lacks it | Section |
|---|---|---|
| `hub/` at the right commit | Submodule pin is 3 months stale; locally it's a symlink | §1 |
| Running mocks on 8000–8004 | Nothing is deployed on a fresh box | §2 |
| `webarena_benchmarks/` | Sibling repo, not a submodule, not tracked | §3 |
| `.env` | Gitignored | §4 |
| Python deps + Chromium | Not vendored | §5 |

---

## 1. `hub/` — check out `594c7b1c`, not the submodule pin

**Do not rely on `git submodule update --init` alone.** It resolves to
`b8207bfc` (2026-05-26), which is three months behind what the tasks were
authored against.

The history is linear, so there is nothing to reconcile — just a stale pointer:

```
b8207bfc (May 26) ──► e40c1188 (Aug 18) ──► 594c7b1c (Aug 27)   ← use this
   ↑ submodule pin      ↑ hub_apps.py HUB_COMMIT
```

```bash
git submodule update --init hub
git -C hub fetch origin webarena
git -C hub checkout 594c7b1c419fd744a5bc2d72e9d0e35b15458bc8
```

**Why `594c7b1c` and not `e40c1188`.** The range contains
`3cfb8909 "webarena mocks: restore four UI paths the agents need"`, which adds
click paths `golden-browser` depends on: the GitLab Settings submenu activating
on `/:ns/:proj/edit`, the Reddit moderators pagination footer, the forum Toolbox
admin path to `/f/<name>/delete`, and the Mod-trash link. Checking out
`e40c1188` would break replays for exactly those task types.

**`hub_apps.py` needs no change.** Its `HUB_COMMIT = "e40c1188..."` string is
stale metadata only. Verified against `594c7b1c`: `deploy-all.sh` is
byte-identical (so port assignment is unchanged), and `APP_DIRS` /
`PLACEHOLDER_MAP` still match the five mocks. TASK.md §8 forbids editing this
file; that still holds.

> On the original machine `hub` is a **symlink** to `/home/ubuntu/CUA-Gym-Hub/`,
> so `git status` there shows `T hub` (typechange). Never `git add hub` on such a
> box — it replaces the submodule entry with a symlink blob.

---

## 2. Deploy the five mocks

Needs Node.js (via nvm) and tmux.

```bash
cd hub && ./deploy-all.sh --no-attach
```

`deploy-all.sh` globs `webarena*_mock` under `websites/` — that matches exactly
5 of the ~100 mocks there, sorted, on ports 8000–8004. This lines up with
`hub_apps.py`'s `8000 + APP_DIRS.index(app_dir)`:

| Port | app_dir | In TASK.md scope |
|---|---|---|
| 8000 | `webarena_classifieds_mock` | no (must still run) |
| 8001 | `webarena_gitlab_mock` | yes — 50 tasks |
| 8002 | `webarena_reddit_mock` | yes — 50 tasks |
| 8003 | `webarena_shopping_admin_mock` | yes — 50 tasks |
| 8004 | `webarena_shopping_mock` | yes — 50 tasks |

First run does `npm install` + `vite build` for 5 apps — budget time. Re-runs can
use `--skip-install --skip-build`. The session is tmux `cua-gym-hub`, one window
per mock, which is what TASK.md §8's `tmux respawn-window -k -t cua-gym-hub:<n>`
recovery step assumes.

Verify:

```bash
for p in 8000 8001 8002 8003 8004; do
  curl -s -o /dev/null -w "$p %{http_code}\n" http://localhost:$p/
done
```

---

## 3. `webarena_benchmarks` — clone as a **sibling**

It is a symlink to `../webarena_benchmarks`, a separate repo — not a submodule,
not tracked. `scripts/sample_webarena_inspirations.py` hardcodes
`PROJECT_ROOT / "webarena_benchmarks" / "webarena.jsonl"`, and TASK.md §5
requires it for inspiration sampling.

```bash
git -C .. clone https://github.com/jayl940712/webarena_benchmarks.git
# verified at 6a29779; the symlink in the repo then resolves
ls -L webarena_benchmarks/webarena.jsonl
```

---

## 4. `.env` — and the precedence trap

`.env` is gitignored. Recreate it from `.env.example`.

> ### Read this before using `--endpoints`
>
> **`.env` outranks `--endpoints`.** `batch_orchestrator.py:load_env()` writes
> every `.env` key into `os.environ` *unconditionally*, and
> `EndpointRegistry.from_sources()` applies environment variables **after** the
> JSON file — so an env var silently overwrites the JSON value.
>
> This means TASK.md §4 step 6's advice ("write `output/endpoints.json` and pass
> it via `--endpoints`") is **not sufficient on its own**. If `.env` still
> carries the old `http://<HUB_HOST>:800X/` endpoints, those win and your
> localhost registry is ignored with no error.
>
> **Set the endpoints in `.env` itself.**

For a self-contained box running its own hub (§2):

```bash
cat > .env <<'EOF'
CUA_GYM_WEBARENA_GITLAB_URL=http://localhost:8001/
CUA_GYM_WEBARENA_REDDIT_URL=http://localhost:8002/
CUA_GYM_WEBARENA_SHOPPING_URL=http://localhost:8004/
CUA_GYM_WEBARENA_SHOPPING_ADMIN_URL=http://localhost:8003/
CUA_GYM_WEBARENA_CLASSIFIEDS_URL=http://localhost:8000/
EOF
```

Note shopping is **8004** and shopping_admin is **8003** — alphabetical order,
easy to transpose.

`OPENAI_API_KEY` in the original `.env` drives an optional offline quality filter
only. Nothing in TASK.md needs it; leave it out rather than copying a secret.

> **Placeholders in the task docs.** The `TASK*.md` files were written against a
> specific deployment, and their hardcoded addresses have been replaced with
> `<HUB_HOST>` (the five WebArena mocks, in TASK.md / TASK2.md / TASK3.md) and
> `<OSM_HOST>` (the OpenStreetMap stack, in TASK_MAP.md). Substitute your own
> host, or `localhost` when running a self-contained box as above. Note that a
> literal `<HUB_HOST>` left in `.env` **passes** `normalize_base_url()` — it is a
> structurally valid URL — and only fails later as a connection error per task.
> Run the §4 resolution check and confirm the printed hosts before launching.

Verify resolution end to end. Note the explicit `load_env()` — nothing loads
`.env` implicitly, only `batch_orchestrator.py` does, so a bare `python3` would
raise `KeyError: no endpoint configured for ...` even with a correct `.env`:

```bash
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from batch_orchestrator import load_env; load_env()
from cua_gym_web.registry import EndpointRegistry
from cuagym.hub_apps import APP_DIRS
r = EndpointRegistry.from_sources()
for a in APP_DIRS: print(a, r.resolve(a).base_url)"
```

All five must print, classifieds included — it is out of scope for task
generation but must still resolve and serve.

---

## 5. Python deps and Chromium

```bash
pip install requests playwright pydantic
python3 -m playwright install chromium
python3 -m pytest tests/ -q     # expect 24 passed
```

`cuagym/requirements.txt` is **not** a pip install target — it is a *manifest*
of what the NeMo runtime venv provides, used by the Phase 2 gate to bound which
third-party imports a bundle may declare. Its `-e nemo-gym[dev] @ ../../` line
will not resolve in a standalone clone, and does not need to.

Also required: the `claude` CLI, authenticated. `batch_orchestrator.py` spawns
`claude --agent orchestrator --dangerously-skip-permissions` per task. The agent
registry travels with the clone — `.claude/settings.json` and all five agent
`.md` files are tracked.

---

## 6. Harness code

The pipeline changes these batches were authored against are on branch
`harness/portable-setup` (commit `a309da8`), not on `main`. Merge or branch from
it. Without it the clone runs an older `scripts/preflight_bundles.py` — the
Phase 2 mechanical gate — missing its reward-structure checks, and a
`cua_gym_web/runner.py` that discards an async replay's return value.

---

## 7. Known gap: TASK.md's reference bundle does not exist

TASK.md §2 cites
`output/task_generation/gitlab-workflows/gitlab_triage_backlog_001/` as the
structural exemplar — "Read it first — it is the shape every one of your 200
tasks must match." **That path no longer exists on any machine, and `output/` is
gitignored, so no clone will ever have it.**

Substitute a verified bundle from a completed run. On the source machine,
`output/runs/bestseller_price_bump_autumn_2022_window_up_8pct_006/` is a
confirmed-good replacement — `## Verdict: PASS`, a passing `verification.json`,
and the full canonical set (`task_instruction.json`, `task.json`, `reward.py`,
`nemo_reward.py`, `nemo_task.json`) plus a `golden_replay.py`. It is strictly
better than the bundle TASK.md cites, which had never been through a Playwright
replay and was only a structural exemplar.

To find others:

```bash
for d in output/runs/*/; do
  [ -f "$d/verification.json" ] && [ -f "$d/task_instruction.json" ] &&
  grep -q '## Verdict: PASS' "$d/REVIEW.md" 2>/dev/null && echo "$d"
done | head
```

On a genuinely fresh box with an empty `output/`, one must be copied from the
source machine — there is no in-repo fallback. Copy it before starting Phase 2,
or the task-authors have no shape to match.

---

## 8. Note on starting fresh

`output/` is gitignored, so a new machine starts with no `batch_status.json` and
no `output/runs/`. `batch_orchestrator.py`'s resumability is per-machine: it skips
a task only when that task's run directory already holds a passing
`verification.json` **and** a `REVIEW.md` with `## Verdict: PASS`. A fresh box
therefore re-runs all 200 from zero. TASK.md §6 is right that this takes many
hours; do not shorten `--timeout` to compensate.

To inherit existing progress instead, copy `output/runs/` and
`output/batch_status.json` across before launching.
