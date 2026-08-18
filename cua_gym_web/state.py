"""Playwright-backed control-plane client for the Hub state API."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from enum import Enum
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from playwright.async_api import APIRequestContext

from .models import SID_RE
from .registry import Endpoint


class SessionMode(str, Enum):
    LEGACY = "legacy"
    HARDENED = "hardened"


class StateApiError(RuntimeError):
    pass


@dataclass(frozen=True)
class SessionHandle:
    mock_name: str
    base_url: str
    sid: str
    mode: SessionMode
    launch_url: str | None = None

    @property
    def browser_sid(self) -> str:
        return "__cua_session__" if self.mode is SessionMode.HARDENED else self.sid


def with_sid(url: str, sid: str) -> str:
    parsed = urlsplit(url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query["sid"] = sid
    return urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path or "/", urlencode(query), parsed.fragment)
    )


class StateClient:
    """Calls setup and reward endpoints through Playwright's request client."""

    def __init__(
        self,
        request: APIRequestContext,
        endpoint: Endpoint,
        mode: SessionMode = SessionMode.LEGACY,
        admin_token: str | None = None,
    ) -> None:
        if mode is SessionMode.HARDENED and not admin_token:
            raise ValueError("hardened mode requires an admin token")
        self.request = request
        self.endpoint = endpoint
        self.mode = mode
        self.admin_token = admin_token

    def _url(self, path: str, sid: str) -> str:
        return with_sid(f"{self.endpoint.base_url}/{path.lstrip('/')}", sid)

    def _headers(self) -> dict[str, str]:
        if self.mode is SessionMode.HARDENED:
            return {"X-CUA-Admin-Token": self.admin_token or ""}
        return {}

    async def _json(
        self,
        method: str,
        path: str,
        sid: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        response = await self.request.fetch(
            self._url(path, sid),
            method=method,
            headers=self._headers(),
            data=payload,
            fail_on_status_code=False,
        )
        text = await response.text()
        if not response.ok:
            raise StateApiError(
                f"{self.endpoint.mock_name} {method} /{path} returned "
                f"HTTP {response.status}: {text[:1000]}"
            )
        try:
            value = await response.json()
        except Exception as exc:
            raise StateApiError(
                f"{self.endpoint.mock_name} {method} /{path} returned non-JSON: {text[:1000]}"
            ) from exc
        if not isinstance(value, dict):
            raise StateApiError(
                f"{self.endpoint.mock_name} {method} /{path} returned "
                f"{type(value).__name__}, expected object"
            )
        return value

    async def go(self, sid: str) -> dict[str, Any]:
        return await self._json("GET", "go", sid)

    async def raw_state(self, sid: str) -> dict[str, Any]:
        return await self._json("GET", "state", sid)

    async def set(self, sid: str, state: dict[str, Any]) -> SessionHandle:
        if not SID_RE.fullmatch(sid):
            raise ValueError(f"invalid SID: {sid!r}")
        result = await self._json(
            "POST", "post", sid, {"action": "set", "state": copy.deepcopy(state)}
        )
        launch_url = result.get("launch_url")
        if launch_url is not None and not isinstance(launch_url, str):
            raise StateApiError("state API returned a non-string launch_url")
        if self.mode is SessionMode.HARDENED and not launch_url:
            raise StateApiError("hardened setup did not return a launch_url")
        return SessionHandle(
            mock_name=self.endpoint.mock_name,
            base_url=self.endpoint.base_url,
            sid=sid,
            mode=self.mode,
            launch_url=launch_url,
        )

    async def set_current(self, sid: str, state: dict[str, Any]) -> None:
        await self._json(
            "POST",
            "post",
            sid,
            {"action": "set_current", "state": copy.deepcopy(state)},
        )

    async def reset(self, sid: str) -> None:
        await self._json("POST", "post", sid, {"action": "reset"})

    async def canonical_default(self, probe_sid: str) -> dict[str, Any]:
        snapshot = await self.go(probe_sid)
        initial = snapshot.get("initial_state")
        current = snapshot.get("current_state")
        if not isinstance(initial, dict) or not isinstance(current, dict):
            raise StateApiError("fresh /go response does not contain object states")
        if initial != current or snapshot.get("state_diff"):
            raise StateApiError("fresh SID is not at a clean default baseline")
        return copy.deepcopy(initial)

    async def establish(
        self, sid: str, state: dict[str, Any]
    ) -> tuple[SessionHandle, dict[str, Any]]:
        handle = await self.set(sid, state)
        snapshot = await self.go(sid)
        initial = snapshot.get("initial_state")
        current = snapshot.get("current_state")
        if not isinstance(initial, dict) or initial != current:
            raise StateApiError("set did not establish equal initial and current state")
        if snapshot.get("state_diff"):
            raise StateApiError("newly established session has a non-empty state diff")
        return handle, snapshot
