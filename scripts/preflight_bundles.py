#!/usr/bin/env python3
"""Mechanical gate over generated WebArena task bundles.

Checks every bundle under the given directories for the canonical files, a
loadable schema-v2 manifest, compilable episode programs, fully resolvable
placeholders, a known app_dir, allowed reward imports, and globally unique
task ids. Prints one line per failing bundle and exits non-zero if any failed.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
import types
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# cuagym/episode_code.py imports its sibling as `resources_servers.cuagym.hub_apps`
# (its NeMo-Gym package path). Alias the local package under that name so the
# real substitute()/placeholder logic is used rather than a reimplementation.
import cuagym.hub_apps as hub_apps  # noqa: E402

_pkg = types.ModuleType("resources_servers")
_pkg.__path__ = []
_sub = types.ModuleType("resources_servers.cuagym")
_sub.__path__ = []
sys.modules.setdefault("resources_servers", _pkg)
sys.modules.setdefault("resources_servers.cuagym", _sub)
sys.modules.setdefault("resources_servers.cuagym.hub_apps", hub_apps)

from cua_gym_web.models import WebTaskManifest  # noqa: E402
from cua_gym_web.reward import (  # noqa: E402
    read_reward_requirements,
    validate_reward_source,
)
from cuagym.episode_code import substitute  # noqa: E402

CANONICAL = ("task_instruction.json", "task.json", "reward.py", "nemo_reward.py", "nemo_task.json")
INSTRUCTION_KEYS = (
    "task_id",
    "task_instruction",
    "app_dir",
    "start_path",
    "difficulty",
    "success_criteria",
)


JS_LITERALS = {"false", "true", "null"}

DIFFICULTIES = {"easy", "medium", "hard"}

# The five hard-criteria defined in TASK2.md 2c. A hard task must satisfy >= 2.
HARD_CRITERIA = {
    "multi_mutation",
    "derived_target",
    "cross_section",
    "exclusion_constraint",
    "shortcut_defeating",
}


def component_weight_total(reward_path: Path) -> float | None:
    """Sum of the declared component weights in a reward.py, or None if absent.

    Rewards declare partial credit as a module-level table of weights. Rather
    than executing the reward, read the literal weights out of the AST: any
    module-level dict/list/tuple whose name mentions COMPONENT/WEIGHT and whose
    numeric leaves are the payouts.
    """
    try:
        tree = ast.parse(reward_path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return None

    def numeric_leaves(node: ast.AST) -> list[float] | None:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return [float(node.value)]
        if isinstance(node, ast.Dict):
            out: list[float] = []
            for value in node.values:
                got = numeric_leaves(value)
                if got is None:
                    return None
                out.extend(got)
            return out
        if isinstance(node, (ast.List, ast.Tuple)):
            out = []
            for value in node.elts:
                got = numeric_leaves(value)
                if got is None:
                    return None
                out.extend(got)
            return out
        return None

    totals: list[float] = []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if not any(("COMPONENT" in n.upper() or "WEIGHT" in n.upper()) for n in names):
            continue
        leaves = numeric_leaves(node.value)
        if leaves:
            totals.append(sum(leaves))
    if not totals:
        return None
    # Prefer a table that already sums to 1.0; otherwise report the first.
    for total in totals:
        if abs(total - 1.0) <= 1e-9:
            return total
    return totals[0]


def js_literal_names(code: str) -> set[str]:
    """Bare `false`/`true`/`null` names that are read but never bound.

    These are what `json.dumps` leaves behind when a JSON fixture is inlined into
    Python source. They parse and compile as ordinary identifiers, so the failure
    only surfaces as a NameError when the episode actually runs.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return set()
    bound: set[str] = set()
    read: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Load):
                read.add(node.id)
            else:
                bound.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bound.add(node.name)
        elif isinstance(node, ast.alias):
            bound.add((node.asname or node.name).split(".")[0])
    return (read & JS_LITERALS) - bound


def broken_inline_json(code: str) -> list[str]:
    """`json.loads("...")` calls whose literal argument is not valid JSON.

    Inlining a JSON fixture into Python source has two failure modes that both
    compile cleanly and only blow up when the episode actually runs:

    * `json.dumps` emits bare `true`/`false`/`null` -- caught by
      `js_literal_names()`;
    * a fixture containing backslash escapes, pasted into a NON-raw triple-quoted
      string, has those escapes eaten by the Python parser before `json.loads`
      ever sees them, so the JSON arrives corrupted. Prefix the literal with `r`.

    Rather than pattern-match the quoting, evaluate the literal the parser
    actually produced and try to parse it. That catches the defect whatever
    caused it.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    problems: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        func = node.func
        name = None
        if isinstance(func, ast.Attribute):
            name = func.attr
        elif isinstance(func, ast.Name):
            name = func.id
        if name != "loads":
            continue
        arg = node.args[0]
        if not (isinstance(arg, ast.Constant) and isinstance(arg.value, str)):
            continue
        line = getattr(node, "lineno", "?")
        try:
            json.loads(arg.value)
        except ValueError as exc:
            problems.append(
                f"line {line}: json.loads() argument is not valid JSON ({exc}); "
                "a non-raw string literal eats backslash escapes -- prefix it with r"
            )
            continue
        # It parses, but a backslash that survived into a NON-raw literal was
        # already rewritten by the Python parser, so the value is silently wrong
        # (a fixture's `\\b` collapses to `\b`, which JSON reads as a backspace).
        # ast.Constant does not record the prefix, so read it off the source.
        if "\\" not in arg.value:
            continue
        segment = ast.get_source_segment(code, arg) or ""
        if not segment[:2].lower().startswith("r"):
            problems.append(
                f"line {line}: json.loads() argument is a non-raw string literal "
                "containing a backslash, so the Python parser rewrote the escape "
                "before json.loads saw it -- prefix the literal with r"
            )
    return problems


def check_bundle(bundle: Path, seen: dict[str, Path]) -> list[str]:
    problems: list[str] = []

    def fail(message: str) -> None:
        problems.append(message)

    for name in CANONICAL:
        if not (bundle / name).is_file():
            fail(f"missing {name}")
    if problems:
        return problems

    try:
        manifest_raw = json.loads((bundle / "task.json").read_text(encoding="utf-8"))
        manifest = WebTaskManifest.from_dict(manifest_raw)
    except Exception as exc:  # noqa: BLE001
        return [f"task.json does not load as WebTaskManifest: {exc}"]

    if manifest.schema_version != 2:
        fail(f"schema_version is {manifest.schema_version}, expected 2")
    if len(manifest.apps) != 1:
        fail(f"{len(manifest.apps)} apps declared; NeMo rows carry exactly one")
    if manifest.task_id != bundle.name:
        fail(f"task_id {manifest.task_id!r} does not match directory {bundle.name!r}")

    for app in manifest.apps:
        if app.name not in hub_apps.APP_DIRS:
            fail(f"app_dir {app.name!r} is not in APP_DIRS")
        expected_env = "CUA_GYM_WEBARENA_" + app.name.removeprefix("webarena_").removesuffix("_mock").upper() + "_URL"
        if app.base_url_env != expected_env:
            fail(f"base_url_env {app.base_url_env!r} should be {expected_env!r}")

    if manifest.task_id in seen:
        fail(f"task_id collides with {seen[manifest.task_id]}")
    else:
        seen[manifest.task_id] = bundle

    try:
        instruction = json.loads((bundle / "task_instruction.json").read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        instruction = None
        fail(f"task_instruction.json is not valid JSON: {exc}")
    if isinstance(instruction, dict):
        for key in INSTRUCTION_KEYS:
            if not instruction.get(key):
                fail(f"task_instruction.json missing {key}")
        if instruction.get("task_id") not in (None, manifest.task_id):
            fail("task_instruction.json task_id disagrees with task.json")
        criteria = instruction.get("success_criteria")
        if not isinstance(criteria, list) or not criteria:
            fail("task_instruction.json success_criteria must be a non-empty list")

    # ---- batch-2 difficulty contract -------------------------------------
    meta = manifest_raw.get("metadata") or {}
    difficulty = (instruction or {}).get("difficulty") if isinstance(instruction, dict) else None
    meta_difficulty = meta.get("difficulty")
    if difficulty not in DIFFICULTIES:
        fail(f"task_instruction.json difficulty {difficulty!r} is not one of {sorted(DIFFICULTIES)}")
    if meta_difficulty != difficulty:
        fail(
            f"task.json metadata.difficulty {meta_difficulty!r} disagrees with "
            f"task_instruction.json {difficulty!r}"
        )
    if difficulty == "hard":
        criteria_list = meta.get("hard_criteria")
        if not isinstance(criteria_list, list) or len(criteria_list) < 2:
            fail("hard task must carry task.json metadata.hard_criteria with >= 2 entries")
        else:
            unknown = [c for c in criteria_list if c not in HARD_CRITERIA]
            if unknown:
                fail(f"unknown hard_criteria {unknown!r}; allowed: {sorted(HARD_CRITERIA)}")
        total = component_weight_total(bundle / manifest.reward_path)
        if total is None:
            fail("hard task reward.py declares no `components` partial credit")
        elif abs(total - 1.0) > 1e-9:
            fail(f"hard task reward components sum to {total!r}, expected exactly 1.0")

    # NeMo row
    try:
        row = json.loads((bundle / "nemo_task.json").read_text(encoding="utf-8"))
        payload = row["task_payload"]
        cuagym_info = payload["cuagym"]
    except Exception as exc:  # noqa: BLE001
        return problems + [f"nemo_task.json is not a valid row payload: {exc}"]

    if cuagym_info.get("app_dir") not in hub_apps.APP_DIRS:
        fail(f"nemo app_dir {cuagym_info.get('app_dir')!r} is not in APP_DIRS")
    if cuagym_info.get("bundle_id") != manifest.task_id:
        fail("nemo bundle_id does not match task_id")
    if payload.get("task_id") != manifest.task_id:
        fail("nemo task_payload.task_id does not match task_id")

    setup_code = cuagym_info.get("initial_setup")
    reward_code = cuagym_info.get("eval_reward_code")

    setup_file = bundle / "initial_setup.py"
    if setup_code is None:
        if setup_file.is_file():
            fail("initial_setup is null in the NeMo row but initial_setup.py exists")
    else:
        if not setup_file.is_file():
            fail("missing initial_setup.py while the NeMo row declares setup code")
        elif setup_file.read_text(encoding="utf-8") != setup_code:
            fail("initial_setup.py does not match the inlined NeMo setup code")

    if reward_code is None:
        fail("nemo eval_reward_code is null")
    elif (bundle / "nemo_reward.py").read_text(encoding="utf-8") != reward_code:
        fail("nemo_reward.py does not match the inlined NeMo reward code")

    for label, code in (("initial_setup", setup_code), ("eval_reward_code", reward_code)):
        if not isinstance(code, str):
            continue
        if "__CUA_GYM_SID__" not in code:
            fail(f"{label} does not contain __CUA_GYM_SID__")
        try:
            resolved = substitute(
                code, sid="gate-sid", hub_base_url="http://localhost", base_port=8000
            )
        except Exception as exc:  # noqa: BLE001
            fail(f"{label} placeholder substitution failed: {exc}")
            continue
        try:
            compile(resolved, f"<{label}>", "exec")
        except SyntaxError as exc:
            fail(f"{label} does not compile: {exc}")
            continue
        # A JSON literal inlined as Python source (e.g. via json.dumps) leaves bare
        # `false`/`true`/`null` names. Those are valid identifiers, so the program
        # compiles cleanly and only raises NameError at episode time.
        for name in js_literal_names(resolved):
            fail(
                f"{label} uses JS literal {name!r} as a bare Python name "
                f"(inline JSON with json.loads, not json.dumps)"
            )
        # Sibling failure mode: the fixture IS parsed with json.loads, but its
        # escapes were eaten by a non-raw triple-quoted string literal.
        for problem in broken_inline_json(resolved):
            fail(f"{label} {problem}")

    if isinstance(setup_code, str):
        for banned in ("launch_gui", "google-chrome", "/tmp/", "webdriver", "playwright"):
            if banned in setup_code:
                fail(f"initial_setup contains forbidden token {banned!r}")
        if "/post?sid=" not in setup_code:
            fail("initial_setup does not POST to /post?sid=")
    if isinstance(reward_code, str):
        if "/go?sid=" not in reward_code:
            fail("eval_reward_code does not GET /go?sid=")
        if "REWARD:" not in reward_code:
            fail("eval_reward_code never prints REWARD:")

    # Offline reward static policy
    requirements = bundle / "requirements.txt"
    if manifest.requirements_path and not (bundle / manifest.requirements_path).is_file():
        fail(f"requirements_path {manifest.requirements_path!r} does not exist")
    try:
        allowed = read_reward_requirements(requirements if requirements.is_file() else None)
        validate_reward_source(
            (bundle / manifest.reward_path).read_text(encoding="utf-8"),
            str(bundle / manifest.reward_path),
            allowed,
        )
    except Exception as exc:  # noqa: BLE001
        fail(f"reward.py failed static validation: {exc}")

    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roots", nargs="+", help="directories holding <task_id>/task.json bundles")
    parser.add_argument("--quiet", action="store_true", help="only print failures")
    parser.add_argument(
        "--prior-batch",
        action="append",
        default=[],
        help=(
            "directory of an earlier, already-delivered batch (e.g. "
            "webarena_08_18_batch_200/tasks). Its task_ids are reserved: a new "
            "bundle that reuses one is a duplicate, not a rename."
        ),
    )
    parser.add_argument(
        "--difficulty-split",
        metavar="E:M:H",
        help=(
            "required per-root difficulty counts, e.g. 1:4:5 for a 10-task batch "
            "or 5:20:25 for a finished site. Checked once per root directory."
        ),
    )
    args = parser.parse_args()

    seen: dict[str, Path] = {}
    for raw in args.prior_batch:
        for path in sorted(Path(raw).resolve().glob("*/*/task.json")):
            seen.setdefault(path.parent.name, path.parent)
        for path in sorted(Path(raw).resolve().glob("*/task.json")):
            seen.setdefault(path.parent.name, path.parent)
    if seen:
        print(f"reserved {len(seen)} task_ids from {len(args.prior_batch)} prior batch root(s)")

    want_split = None
    if args.difficulty_split:
        e, m, h = (int(x) for x in args.difficulty_split.split(":"))
        want_split = {"easy": e, "medium": m, "hard": h}

    failed = 0
    total = 0
    for raw in args.roots:
        root = Path(raw).resolve()
        if (root / "task.json").is_file():
            bundles = [root]
        else:
            bundles = sorted(p.parent for p in root.glob("*/task.json"))
        total += len(bundles)

        split = {"easy": 0, "medium": 0, "hard": 0}
        for bundle in bundles:
            problems = check_bundle(bundle, seen)
            try:
                d = json.loads((bundle / "task_instruction.json").read_text())["difficulty"]
                if d in split:
                    split[d] += 1
            except Exception:  # noqa: BLE001 - already reported by check_bundle
                pass
            if problems:
                failed += 1
                print(f"FAIL {bundle}")
                for problem in problems:
                    print(f"     - {problem}")
            elif not args.quiet:
                print(f"PASS {bundle}")

        if want_split is not None and split != want_split:
            failed += 1
            print(f"FAIL {root}")
            print(
                f"     - difficulty split is "
                f"{split['easy']}:{split['medium']}:{split['hard']} (easy:medium:hard), "
                f"required {args.difficulty_split}"
            )

    print(f"\n{total - failed}/{total} bundles passed the gate")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
