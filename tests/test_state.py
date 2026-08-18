import asyncio

import pytest

from cua_gym_web.registry import Endpoint
from cua_gym_web.state import SessionMode, StateClient, with_sid


class FakeResponse:
    def __init__(self, value, status=200):
        self.value = value
        self.status = status
        self.ok = 200 <= status < 300

    async def text(self):
        return "response"

    async def json(self):
        return self.value


class FakeRequest:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    async def fetch(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return FakeResponse(self.responses.pop(0))


def endpoint():
    return Endpoint("webarena_gitlab_mock", "https://gitlab.example.test")


def test_with_sid_preserves_existing_query():
    result = with_sid(
        "https://gitlab.example.test/issues?sort=asc&page=2", "task_sid"
    )

    assert "sort=asc" in result
    assert "page=2" in result
    assert "sid=task_sid" in result


def test_establish_requires_clean_baseline():
    state = {"issues": []}
    request = FakeRequest(
        [
            {"success": True},
            {
                "initial_state": state,
                "current_state": state,
                "state_diff": {},
            },
        ]
    )
    client = StateClient(request, endpoint())

    handle, snapshot = asyncio.run(client.establish("task_sid", state))

    assert handle.sid == "task_sid"
    assert snapshot["initial_state"] == state
    assert request.calls[0][1]["data"]["action"] == "set"


def test_hardened_setup_requires_launch_url():
    request = FakeRequest([{"success": True}])
    client = StateClient(
        request,
        endpoint(),
        mode=SessionMode.HARDENED,
        admin_token="secret",
    )

    with pytest.raises(Exception, match="launch_url"):
        asyncio.run(client.set("task_sid", {}))
