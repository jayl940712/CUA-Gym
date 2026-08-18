"""Deployment-independent endpoint registry for WebArena mocks."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
from urllib.parse import urlsplit, urlunsplit

from .models import AppSpec, endpoint_env_name


def normalize_base_url(value: str) -> str:
    parsed = urlsplit(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"endpoint must be an absolute HTTP(S) URL: {value!r}")
    if parsed.query or parsed.fragment:
        raise ValueError(f"endpoint cannot include query or fragment: {value!r}")
    return urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", "")
    )


@dataclass(frozen=True)
class Endpoint:
    mock_name: str
    base_url: str


class EndpointRegistry:
    """Resolve mock names without embedding deployment URLs in task bundles."""

    def __init__(self, values: Mapping[str, str] | None = None) -> None:
        self._values = {
            key: normalize_base_url(value)
            for key, value in (values or {}).items()
            if value
        }

    @classmethod
    def from_sources(
        cls,
        config_path: str | Path | None = None,
        environ: Mapping[str, str] | None = None,
    ) -> "EndpointRegistry":
        values: dict[str, str] = {}
        if config_path:
            raw = json.loads(Path(config_path).read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise ValueError("endpoint registry JSON must be an object")
            values.update({str(key): str(value) for key, value in raw.items()})
        env = environ if environ is not None else os.environ
        for key, value in env.items():
            if key.startswith("CUA_GYM_WEBARENA_") and key.endswith("_URL") and value:
                values[key] = value
        return cls(values)

    def resolve(self, app: AppSpec | str) -> Endpoint:
        mock_name = app.name if isinstance(app, AppSpec) else app
        env_name = app.base_url_env if isinstance(app, AppSpec) else endpoint_env_name(app)
        value = self._values.get(mock_name) or self._values.get(env_name)
        if not value:
            raise KeyError(
                f"no endpoint configured for {mock_name}; set {env_name} "
                "or add the mock name to the endpoint registry JSON"
            )
        return Endpoint(mock_name=mock_name, base_url=value)

    def validate_apps(self, apps: tuple[AppSpec, ...]) -> dict[str, Endpoint]:
        return {app.name: self.resolve(app) for app in apps}
