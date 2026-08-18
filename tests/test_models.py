import json

import pytest

from cua_gym_web.models import AppSpec, WebTaskManifest, endpoint_env_name
from cua_gym_web.registry import EndpointRegistry


def test_manifest_round_trip(tmp_path):
    task = WebTaskManifest(
        task_id="webarena-1",
        instruction="Open the project issue.",
        apps=(AppSpec.for_source("gitlab", "/project/issues/1"),),
        source_evaluator={"eval_types": ["url_match"]},
    )
    path = tmp_path / "task.json"
    task.write(path)

    assert WebTaskManifest.read(path) == task
    assert json.loads(path.read_text())["schema_version"] == 2


def test_endpoint_registry_prefers_deployment_configuration():
    app = AppSpec.for_source("shopping_admin")
    env_key = endpoint_env_name(app.name)
    registry = EndpointRegistry.from_sources(
        environ={env_key: "https://admin.example.test/"}
    )

    assert registry.resolve(app).base_url == "https://admin.example.test"


def test_manifest_rejects_non_webarena_mock():
    with pytest.raises(ValueError, match="invalid WebArena mock"):
        AppSpec(
            name="gitlab_mock",
            source_name="gitlab",
            base_url_env="CUA_GYM_GITLAB_URL",
        )
