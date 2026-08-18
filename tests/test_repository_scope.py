import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_root_agent_system_is_webarena_only():
    settings = json.loads((ROOT / ".claude" / "settings.json").read_text())

    assert set(settings["agents"]) == {
        "orchestrator",
        "golden-browser",
        "reward-gen",
        "reward-audit",
    }
    assert list((ROOT / ".claude" / "skills").glob("*/SKILL.md")) == [
        ROOT / ".claude" / "skills" / "webarena" / "SKILL.md"
    ]


def test_vm_entrypoints_are_removed():
    assert not (ROOT / "scripts" / "env_cli.py").exists()
    assert not (ROOT / "utils" / "env.py").exists()
    assert not any((ROOT / "utils").glob("*.py"))


def test_reward_runtime_has_no_semantic_judge_module():
    assert not (ROOT / "cua_gym_web" / "judge.py").exists()
    assert not (ROOT / "cua_gym_web" / "evaluator.py").exists()
    assert (ROOT / "cua_gym_web" / "reward.py").is_file()
    runtime = "\n".join(
        path.read_text(errors="ignore")
        for path in (ROOT / "cua_gym_web").glob("*.py")
    ).casefold()
    assert "openai" not in runtime
    assert "anthropic" not in runtime
