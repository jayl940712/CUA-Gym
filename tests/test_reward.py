import asyncio

import pytest

from cua_gym_web.compiler import render_reward
from cua_gym_web.reward import (
    PythonRewardRunner,
    RewardValidationError,
    read_reward_requirements,
    validate_reward_source,
)


def run_reward(tmp_path, evaluator, evidence):
    path = tmp_path / "reward.py"
    path.write_text(render_reward(evaluator))
    return asyncio.run(PythonRewardRunner().evaluate(path, evidence))


def test_compiled_url_reward_uses_immutable_final_url(tmp_path):
    result = run_reward(
        tmp_path,
        {
            "eval_types": ["url_match"],
            "reference_url": "__GITLAB__/dashboard/todos",
            "url_note": "GOLD in PRED",
        },
        {
            "apps": {
                "gitlab": {
                    "final_urls": [
                        "https://mock.test/dashboard/todos?sid=private"
                    ]
                }
            }
        },
    )

    assert result.score == 1.0


def test_compiled_dom_reward_checks_collected_observation(tmp_path):
    result = run_reward(
        tmp_path,
        {
            "eval_types": ["program_html"],
            "program_html": [
                {
                    "url": "last",
                    "locator": "document.body.innerText",
                    "required_contents": {
                        "must_include": ["CUA verification issue"]
                    },
                }
            ],
        },
        {
            "apps": {},
            "observations": [
                {
                    "index": 0,
                    "content": "Issues\nCUA verification issue",
                }
            ],
        },
    )

    assert result.score == 1.0


def test_reward_policy_rejects_network_and_filesystem_code():
    with pytest.raises(RewardValidationError, match="forbidden module"):
        validate_reward_source(
            "import requests\n\ndef evaluate(evidence):\n    return 1.0\n"
        )
    with pytest.raises(RewardValidationError, match="forbidden function"):
        validate_reward_source(
            "def evaluate(evidence):\n    open('/tmp/result', 'w')\n    return 1.0\n"
        )


def test_popular_third_party_import_requires_declaration(tmp_path):
    source = "import numpy\n\ndef evaluate(evidence):\n    return 0.0\n"
    with pytest.raises(RewardValidationError, match="forbidden module"):
        validate_reward_source(source)

    requirements = tmp_path / "requirements.txt"
    requirements.write_text("numpy>=1.24\n")
    allowed = read_reward_requirements(requirements)

    assert allowed == {"numpy"}
    validate_reward_source(source, allowed_third_party=allowed)


def test_requirements_reject_non_allowlisted_packages(tmp_path):
    requirements = tmp_path / "requirements.txt"
    requirements.write_text("requests==2.32.0\n")

    with pytest.raises(RewardValidationError, match="unsupported package"):
        read_reward_requirements(requirements)


def test_local_sibling_import_is_forbidden_even_if_file_exists(tmp_path):
    (tmp_path / "helper.py").write_text("VALUE = 1\n")
    source = "import helper\n\ndef evaluate(evidence):\n    return helper.VALUE\n"

    with pytest.raises(RewardValidationError, match="forbidden module"):
        validate_reward_source(source)
