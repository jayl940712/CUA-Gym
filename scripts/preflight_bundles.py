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
import builtins
import json
import re
import unicodedata
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
# TASK4.md S4 names five hard criteria in prose; batches 2-3 encoded a partly
# different set, and this enum was never reconciled. Authors follow S4 (it is
# what the lane briefs cite) and were failing on `ordering_dependency` and
# `cross_page`, which S4 lists and this set omitted. Both vocabularies are
# accepted: the S4 names are canonical for new work, the legacy three are kept
# so the three prior snapshots still validate.
HARD_CRITERIA_CANONICAL = {
    "multi_entity",          # S4.1 three or more distinct records mutated
    "derived_target",        # S4.2 target identified by a computed property
    "ordering_dependency",   # S4.3 an earlier step unlocks or constrains a later one
    "cross_page",            # S4.4 work spans three or more distinct pages
    "conditional_branch",    # S4.5 what to do depends on state read first
}
HARD_CRITERIA_LEGACY = {
    "multi_mutation",        # batch-2/3 spelling of multi_entity
    "cross_section",         # batch-2/3 spelling of cross_page
    "exclusion_constraint",  # batch-2/3 only; forbidden in the terse set (S3.2)
    "shortcut_defeating",    # batch-2/3 only
}
HARD_CRITERIA = HARD_CRITERIA_CANONICAL | HARD_CRITERIA_LEGACY


def _dict_from_node(node: ast.AST) -> dict | None:
    """The dict a module-level assignment produces, literal or JSON.

    TASK4 S7 requires inline fixtures to be written as json.loads() over a raw
    triple-quoted literal, so a reward that follows the rules does NOT expose
    an `ast.Dict` at all. Reading
    only literals therefore skipped exactly the conforming bundles -- silently,
    which is the worst way to skip them: the hard-task weight check reported a
    missing components table that was right there, and the terse preservation
    check became a no-op rather than a failure.
    """
    if isinstance(node, ast.Dict):
        try:
            return ast.literal_eval(node)
        except (ValueError, SyntaxError):
            return None
    # json.loads("...") / json.loads(r"""...""")
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "loads"
        and node.args
        and isinstance(node.args[0], ast.Constant)
        and isinstance(node.args[0].value, str)
    ):
        try:
            value = json.loads(node.args[0].value)
        except ValueError:
            return None
        return value if isinstance(value, dict) else None
    return None


def _weight_tables(reward_path: Path) -> list[dict]:
    """Every module-level COMPONENT*/WEIGHT* mapping in a reward.py."""
    try:
        tree = ast.parse(reward_path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return []
    tables = []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(t, ast.Name) and ("COMPONENT" in t.id.upper() or "WEIGHT" in t.id.upper())
            for t in node.targets
        ):
            continue
        table = _dict_from_node(node.value)
        if table is not None:
            tables.append(table)
    return tables


def component_weight_total(reward_path: Path) -> float | None:
    """Sum of the declared component weights in a reward.py, or None if absent.

    Rewards declare partial credit as a module-level table of weights. Rather
    than executing the reward, read the literal weights out of the AST: any
    module-level dict/list/tuple whose name mentions COMPONENT/WEIGHT and whose
    numeric leaves are the payouts.
    """
    # A conforming reward writes this table as json.loads(r"""..."""), which
    # has no ast.Dict to read. Try that first; fall back to the literal walk
    # for the older hand-written tables.
    tables = _weight_tables(reward_path)
    if tables:
        values = [v for t in tables for v in t.values() if isinstance(v, (int, float))]
        if values:
            return float(sum(values))

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


# ---- batch-4 style contract (TASK4.md S3) --------------------------------

STYLES = {"terse", "explicit"}

TERSE_MAX_WORDS = 40

# S3.2: in the terse set every weighted component must name something the model
# MADE TRUE. A component that pays because something did not change is
# forbidden. Detected off the component name, which is what an auditor reads.
PRESERVATION_TOKENS = (
    "untouched", "unchanged", "preserved", "preservation", "survived", "survives",
    "intact", "not_deleted", "not_removed", "not_modified", "still_", "_still",
    "_kept", "kept_", "remains_", "_remains", "left_alone", "no_other", "others_",
    "undisturbed", "_undisturbed", "unaffected", "unmodified", "retained",
)


def component_names(reward_path: Path) -> list[str]:
    """Keys of the module-level COMPONENT_WEIGHTS table, read out of the AST."""
    try:
        tree = ast.parse(reward_path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return []
    names: list[str] = []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(t, ast.Name) and ("COMPONENT" in t.id.upper() or "WEIGHT" in t.id.upper())
            for t in node.targets
        ):
            continue
        # Literal dict, or the json.loads(r"""...""") form TASK4 S7 mandates.
        table = _dict_from_node(node.value)
        if table is not None:
            names.extend(k for k in table if isinstance(k, str))
    return names


def preservation_components(reward_path: Path) -> list[str]:
    return [
        name for name in component_names(reward_path)
        if any(token in name.lower() for token in PRESERVATION_TOKENS)
    ]


def reads_initial_state(reward_path: Path) -> bool:
    """True when reward.py reads `initial_state` as data, not just in prose.

    S7: "Every reward reads `current_state` only; never diff against
    `initial_state`." This is the *logic* half of the preservation check that a
    name-only scan cannot reach -- a component called `branch_created` that is
    really `initial != current` still pays for a diff.

    It must be an AST check, not a grep: 261 of batch 3's 600 rewards mention
    `initial_state` and only 50 actually read it, because the rest are comments
    asserting that they do not. A grep would over-fire five times over.
    """
    try:
        tree = ast.parse(reward_path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return False
    return any(
        isinstance(node, ast.Constant) and node.value == "initial_state"
        for node in ast.walk(tree)
    )


def unbound_names(code: str) -> set[str]:
    """Names read but never bound, imported, or built in (TASK4.md S10.4).

    `compile()` and `validate_reward_source` both accept a program that
    references a constant it never defines; the NameError fires only at episode
    time, and only on the branch that reaches it. A batch-3 variant shipped an
    undefined `SEEDED_ORDER_COUNT` and scored a clean 0.0 at t=0 because the
    enclosing check short-circuited -- so it blew up *only on a correct replay*.
    This generalises `js_literal_names()` from three names to every name.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return set()

    bound: set[str] = set()
    read: set[str] = set()

    def bind_args(args: ast.arguments) -> None:
        for group in (args.posonlyargs, args.args, args.kwonlyargs):
            bound.update(a.arg for a in group)
        for extra in (args.vararg, args.kwarg):
            if extra is not None:
                bound.add(extra.arg)

    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            (read if isinstance(node.ctx, ast.Load) else bound).add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            bound.add(node.name)
            bind_args(node.args)
        elif isinstance(node, ast.Lambda):
            bind_args(node.args)
        elif isinstance(node, ast.ClassDef):
            bound.add(node.name)
        elif isinstance(node, ast.alias):
            bound.add((node.asname or node.name).split(".")[0])
        elif isinstance(node, ast.ExceptHandler) and node.name:
            bound.add(node.name)
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            bound.update(node.names)
        elif isinstance(node, ast.MatchAs) and node.name:
            bound.add(node.name)

    return read - bound - set(dir(builtins))


# ---- batch-5 skill contract (docs/SKILL_TAXONOMY.md) ---------------------

RETRIEVAL_SKILLS = {f"R{i}" for i in range(1, 11)}
ACTION_SKILLS = {f"A{i}" for i in range(1, 14)}
ALL_SKILLS = RETRIEVAL_SKILLS | ACTION_SKILLS

BENCHMARK = Path("webarena_benchmarks/webarena.jsonl")


def _normalise_intent(text: str) -> str:
    """Compare intents ignoring whitespace, case, punctuation and ACCENTS.

    Authors copy analogues out of a terminal, so a verbatim match on the raw
    string would fail on a collapsed newline and teach them to stop quoting.

    Accent folding was added after a lane transcribed the official intent
    "Invite Benoît Blanchon ..." as "Benoit" and had all ten of its bundles
    rejected. Without folding, `î` is not in [a-z0-9] and collapses to a space,
    so "beno t blanchon" fails to match "benoit blanchon" -- a transcription
    artefact, not a paraphrase. The check exists to catch invented or reworded
    analogues, and it still does: every other character must line up exactly.
    """
    folded = unicodedata.normalize("NFKD", str(text))
    folded = "".join(c for c in folded if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", folded.lower()).strip()


def _load_official_intents() -> set[str] | None:
    """Every official intent, normalised. None when the corpus is unavailable.

    None disables the analogue cross-check rather than failing every bundle:
    a missing benchmark file is an environment problem, and turning it into 600
    identical failures would bury the real ones.
    """
    if not BENCHMARK.is_file():
        return None
    intents: set[str] = set()
    for line in BENCHMARK.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            intents.add(_normalise_intent(json.loads(line)["ques"]))
        except Exception:  # noqa: BLE001
            continue
    return intents or None


OFFICIAL_INTENTS = _load_official_intents()

# Set by --medium-is-exactly-two; off by default so the three prior
# snapshots and batch 5 still validate unchanged.
MEDIUM_IS_EXACTLY_TWO = False


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

    # ---- batch-4 style contract (TASK4.md S3) ----------------------------
    reward_path = bundle / manifest.reward_path
    style = meta.get("style")
    if style is None:
        fail("task.json metadata.style is missing; must be 'terse' or 'explicit'")
    elif style not in STYLES:
        fail(f"task.json metadata.style {style!r} is not one of {sorted(STYLES)}")
    elif style == "terse":
        text = (instruction or {}).get("task_instruction") or ""
        words = len(str(text).split())
        if words > TERSE_MAX_WORDS:
            fail(f"terse instruction is {words} words, over the {TERSE_MAX_WORDS}-word cap (S3.1)")
        leaks = preservation_components(reward_path)
        if leaks:
            fail(
                f"terse reward pays for inaction via component(s) {leaks!r}; assert the "
                "exact resulting collection instead (S3.2/S3.3)"
            )
        if "exclusion_constraint" in (meta.get("hard_criteria") or []):
            fail(
                "terse task claims hard_criteria 'exclusion_constraint', which scores the "
                "untouched part and is unavailable in the terse set (S3.2)"
            )

    # S7: rewards read current_state only. This is the logic half of S3.2 --
    # a neutrally-named component that is really `initial != current` still
    # pays for a diff, and no name scan can see it.
    if reads_initial_state(reward_path):
        fail(
            "reward.py reads `initial_state`; every reward must read `current_state` "
            "only and never diff against the baseline (S7)"
        )

    # ---- batch-5 skill contract (docs/SKILL_TAXONOMY.md) ------------------
    # Batches 1-4 chose tasks by topic and only ever checked intent *shape*.
    # A task can look like a WebArena task, score like one, and exercise no
    # skill the benchmark exercises -- skill is what transfers, so it is now
    # recorded per bundle and gated here rather than asserted in a report.
    skills = meta.get("skills")
    if skills is None:
        fail(
            "task.json metadata.skills is missing; list the skill ids this task "
            f"exercises, drawn from {sorted(RETRIEVAL_SKILLS | ACTION_SKILLS)}"
        )
    elif not isinstance(skills, list) or not skills:
        fail(f"task.json metadata.skills must be a non-empty list, got {skills!r}")
    else:
        unknown = [s for s in skills if s not in ALL_SKILLS]
        if unknown:
            fail(
                f"task.json metadata.skills contains unknown id(s) {unknown!r}; "
                "valid ids are defined in docs/SKILL_TAXONOMY.md"
            )
        elif len(set(skills)) != len(skills):
            fail(f"task.json metadata.skills repeats an id: {skills!r}")
        else:
            # Difficulty is derived from the chain this round rather than
            # imposed as a quota, so the two must actually agree. A "hard"
            # task built from one retrieval and one action is a medium whose
            # label drifted -- the exact error batch 4 spent time on.
            retrieval = [s for s in skills if s in RETRIEVAL_SKILLS]
            action = [s for s in skills if s in ACTION_SKILLS]
            if not action:
                fail(
                    f"metadata.skills {skills!r} names no action skill; a task with "
                    "no mutation has no verifiable writeback (S3.5)"
                )
            if not retrieval:
                fail(
                    f"metadata.skills {skills!r} names no retrieval skill; the target "
                    "must be derived from the site, not handed over in the instruction"
                )
            # Batch 6 is all-medium by request, and a "medium" there is
            # exactly one retrieval feeding one action. Without this, a 3-skill
            # chain labelled medium passes -- which is a hard task wearing the
            # wrong label, and the whole point of an all-medium batch is that
            # the difficulty is uniform.
            if MEDIUM_IS_EXACTLY_TWO and difficulty == "medium" and len(skills) != 2:
                fail(
                    f"medium task declares {len(skills)} skills {skills!r}; this batch "
                    "requires exactly one retrieval and one action. Split it into two "
                    "tasks or drop a step -- do not relabel it hard"
                )
            if difficulty == "medium" and len(skills) < 2:
                fail(
                    f"medium task exercises {len(skills)} skill(s); a medium is at "
                    "least one retrieval feeding one action"
                )
            if difficulty == "hard" and len(skills) < 3:
                fail(
                    f"hard task exercises only {len(skills)} skill(s) {skills!r}; a hard "
                    "task is a chain of 3+ where each step's output constrains the next. "
                    "Relabel it medium rather than padding the list"
                )
            if difficulty == "hard" and len(retrieval) < 2 and len(action) < 2:
                fail(
                    f"hard task {skills!r} has one retrieval and one action padded to "
                    "three; a hard chain needs either two distinct retrievals or one "
                    "retrieval feeding two dependent actions"
                )

    # Resembling an official task is the point of batch 5. Reproducing one
    # verbatim is contamination: the benchmark is the evaluation set, and a
    # word-for-word row in the training data raises the measured score without
    # adding capability.
    if OFFICIAL_INTENTS is not None:
        intent_text = (instruction or {}).get("task_instruction") or ""
        if _normalise_intent(intent_text) in OFFICIAL_INTENTS:
            fail(
                "task_instruction reproduces an official benchmark intent verbatim, "
                "which contaminates the evaluation set. Keep the skill and the shape; "
                "change the entities and values"
            )

    # Batch 5 uses `initial_setup.py` deliberately -- to break ties, plant
    # distractors, and give conditional branches something real to branch on.
    # That changes what the task is evidence of (moderation GIVEN rights is not
    # the acquisition of rights), so it may not be silent.
    if (bundle / "initial_setup.py").is_file():
        injected = meta.get("injected_preconditions")
        if not isinstance(injected, list) or not injected:
            fail(
                "bundle ships initial_setup.py but task.json metadata."
                "injected_preconditions is missing or empty; list what state was "
                "written and why, e.g. ['moderatorOf: [\"DIY\"] — the 95 seeded "
                "forums have no moderators, so forum edit 403s without it']"
            )
        elif not all(isinstance(entry, str) and entry.strip() for entry in injected):
            fail(
                f"metadata.injected_preconditions must be a list of non-empty "
                f"strings, got {injected!r}"
            )

    chain = meta.get("skill_chain")
    if not isinstance(chain, str) or not chain.strip():
        fail(
            "task.json metadata.skill_chain is missing; state in one line how each "
            "step's output feeds the next, e.g. 'date-range report -> sum -> write "
            "the figure into a CMS block'"
        )

    # The honesty check. An author who cannot name a real benchmark task the
    # design is aimed at has not built an in-distribution task, and inventing
    # an analogue is worse than admitting there is none.
    analogues = meta.get("official_analogues")
    if not isinstance(analogues, list) or not analogues:
        fail(
            "task.json metadata.official_analogues is missing; quote at least one "
            "real intent from webarena_benchmarks/webarena.jsonl this task is "
            "in-distribution with"
        )
    elif OFFICIAL_INTENTS is not None:
        missing = [a for a in analogues if _normalise_intent(a) not in OFFICIAL_INTENTS]
        if missing:
            fail(
                f"metadata.official_analogues entries not found in the benchmark "
                f"corpus: {missing!r}. Quote the intent verbatim, do not paraphrase "
                "or invent one"
            )

    # ---- batch-4 start_path contract (TASK4.md S5) -----------------------
    start_path = (instruction or {}).get("start_path")
    if isinstance(start_path, str):
        if not start_path.startswith("/"):
            fail(f"start_path {start_path!r} must begin with '/'")
        for app in manifest.apps:
            if app.start_path != start_path:
                fail(
                    f"task.json apps[].start_path {app.start_path!r} disagrees with "
                    f"task_instruction.json start_path {start_path!r}"
                )

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
        # A name read but never bound compiles and passes static validation, then
        # raises NameError at runtime -- often only on the branch a *correct*
        # rollout reaches.
        missing = unbound_names(resolved)
        if missing:
            fail(f"{label} references undefined name(s): {sorted(missing)}")

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
        "--medium-is-exactly-two",
        action="store_true",
        help="a `medium` task must declare exactly 2 skills (1 retrieval + 1 action)",
    )
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
    parser.add_argument(
        "--style-split",
        metavar="TERSE:EXPLICIT",
        help="required per-root metadata.style counts, e.g. 113:37 (TASK4.md S3.4)",
    )
    parser.add_argument(
        "--root-start-min",
        type=float,
        metavar="PCT",
        help=(
            "minimum share of bundles in each root whose start_path is '/'. "
            "TASK4.md S5.1 sets the batch floor at 70 and the per-site floor at 60."
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

    want_style = None
    if args.style_split:
        t, x = (int(v) for v in args.style_split.split(":"))
        want_style = {"terse": t, "explicit": x}

    failed = 0
    root_failures = 0
    total = 0
    for raw in args.roots:
        root = Path(raw).resolve()
        if (root / "task.json").is_file():
            bundles = [root]
        else:
            bundles = sorted(p.parent for p in root.glob("*/task.json"))
        total += len(bundles)

        split = {"easy": 0, "medium": 0, "hard": 0}
        styles = {"terse": 0, "explicit": 0}
        root_starts = 0
        retrieval = 0
        deep_starts: list[str] = []
        for bundle in bundles:
            problems = check_bundle(bundle, seen)
            try:
                inst = json.loads((bundle / "task_instruction.json").read_text())
                meta = json.loads((bundle / "task.json").read_text()).get("metadata") or {}
                d = inst["difficulty"]
                if d in split:
                    split[d] += 1
                if meta.get("style") in styles:
                    styles[meta["style"]] += 1
                if meta.get("shape") == "retrieval_writeback":
                    retrieval += 1
                if inst.get("start_path") == "/":
                    root_starts += 1
                else:
                    deep_starts.append(f"{bundle.name} -> {inst.get('start_path')!r}")
            except Exception:  # noqa: BLE001 - already reported by check_bundle
                pass
            if problems:
                failed += 1
                print(f"FAIL {bundle}")
                for problem in problems:
                    print(f"     - {problem}")
            elif not args.quiet:
                print(f"PASS {bundle}")

        if bundles:
            pct = 100.0 * root_starts / len(bundles)
            print(
                f"{root.name}: {len(bundles)} bundles | "
                f"difficulty {split['easy']}:{split['medium']}:{split['hard']} | "
                f"style {styles['terse']}T/{styles['explicit']}E | "
                f"start_path='/' {root_starts}/{len(bundles)} ({pct:.1f}%) | "
                f"retrieval_writeback {retrieval}"
            )
            if args.root_start_min is not None and pct < args.root_start_min:
                root_failures += 1
                print(f"FAIL {root}")
                print(
                    f"     - only {pct:.1f}% of bundles start at '/', below the required "
                    f"{args.root_start_min:.0f}% (TASK4.md S5.1)"
                )
                for line in deep_starts[:20]:
                    print(f"       deep: {line}")

        if want_style is not None and styles != want_style:
            root_failures += 1
            print(f"FAIL {root}")
            print(
                f"     - style split is {styles['terse']} terse / {styles['explicit']} "
                f"explicit, required {args.style_split}"
            )

        if want_split is not None and split != want_split:
            root_failures += 1
            print(f"FAIL {root}")
            print(
                f"     - difficulty split is "
                f"{split['easy']}:{split['medium']}:{split['hard']} (easy:medium:hard), "
                f"required {args.difficulty_split}"
            )

    print(f"\n{total - failed}/{total} bundles passed the gate")
    if root_failures:
        print(f"{root_failures} corpus-level requirement(s) unmet (split / style / start_path)")
    return 1 if (failed or root_failures) else 0


if __name__ == "__main__":
    raise SystemExit(main())
