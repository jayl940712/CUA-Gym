import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_root_agent_system_is_webarena_only():
    settings = json.loads((ROOT / ".claude" / "settings.json").read_text())

    assert set(settings["agents"]) == {
        "task-author",
        "orchestrator",
        "golden-browser",
        "reward-gen",
        "reward-audit",
    }
    assert list((ROOT / ".claude" / "skills").glob("*/SKILL.md")) == [
        ROOT / ".claude" / "skills" / "webarena" / "SKILL.md"
    ]
    for agent_name, config in settings["agents"].items():
        prompt = (ROOT / config["prompt"]).read_text()
        assert f"name: {agent_name}" in prompt.split("---", 2)[1]


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


def test_agent_prompts_require_nemo_inline_episode_contract():
    author = (ROOT / ".claude" / "agents" / "task-author.md").read_text()
    reward = (ROOT / ".claude" / "agents" / "reward-gen.md").read_text()

    for token in (
        "cuagym/hub_apps.py",
        "__CUA_GYM_SID__",
        "task_instruction.json",
        "initial_setup",
        "eval_reward_code",
        "nemo_tasks.jsonl",
    ):
        assert token in author
    assert "/go?sid=" in reward
    assert "REWARD: <float>" in reward
