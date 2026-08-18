# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Schemas for the CUA-Gym-Hub resources server.

The server speaks the exact seed/step/verify/close protocol that
``responses_api_agents/web_agent`` already uses against the WebArena server, so
all request/response models are reused from ``resources_servers.webarena``.
Task rows therefore validate as ``WebArenaTaskRow`` (the ``eval`` block is an
inert stub — verification is the row's inlined reward program) and carry their
CUA-Gym specifics in the extra ``cuagym`` field.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self

from resources_servers.webarena.schemas import (
    WebArenaResourcesServerConfig,
    WebArenaTaskRow,
)


# Inert eval stub for rows: web_agent validates task rows as WebArenaTaskRow,
# whose eval.eval_types must be a known Classic WebArena evaluator. The cuagym
# server never reads it; reward comes from the row's inlined reward program.
CUAGYM_EVAL_STUB: dict[str, Any] = {
    "eval_types": ["string_match"],
    "reference_answers": None,
    "note": "unused — CUA-Gym reward code is authoritative",
}


class CuaGymTaskInfo(BaseModel):
    """The `cuagym` extra field carried inside a task row.

    ``initial_setup`` and ``eval_reward_code`` are self-contained Python
    programs produced by the dataset converter: sid appears only as the
    ``__CUA_GYM_SID__`` placeholder and hub endpoints as
    ``__CUA_GYM_<APP>_URL__`` placeholders, both filled by the server at
    episode time. ``bundle_id`` is provenance only.
    """

    bundle_id: str
    app_dir: str
    eval_reward_code: str
    initial_setup: str | None = None


class CuaGymResourcesServerConfig(WebArenaResourcesServerConfig):
    """WebArena browser-pool config plus CUA-Gym-Hub wiring.

    ``site_urls``/``credentials``/``judge_*`` fields are inherited but unused —
    the hub needs no login and rewards come from row-inlined programs.
    ``hub_base_url`` is substituted into those programs at episode time, so
    rotating the (ephemeral) hub IP is a one-line config change and never
    requires reconverting data.
    """

    hub_base_url: str = "http://localhost"
    hub_base_port: int = Field(default=8000, ge=1)
    node_placement_strategy: Literal["spread_all", "spread_gen"] = Field(
        default="spread_all",
        description=(
            "spread_all distributes browser actors across every Ray node; "
            "spread_gen restricts them to runtime generation nodes"
        ),
    )
    # Defaults must stay strictly inside the inherited browser budgets
    # (browser_operation_timeout_seconds=180, browser_evaluation_timeout_seconds=300);
    # see normalize_hub_config.
    setup_timeout_seconds: float = Field(default=90.0, gt=0)
    reward_timeout_seconds: float = Field(default=120.0, gt=0)

    @model_validator(mode="after")
    def normalize_hub_config(self) -> Self:
        self.hub_base_url = self.hub_base_url.rstrip("/")
        # Setup runs inside /seed_session and reward inside /verify, both of
        # which the base server bounds with its own browser budgets. If the
        # inner budget is not strictly smaller, the outer wait_for fires first
        # and the episode fails as a generic timeout instead of reporting the
        # program's own failure (and the browser lease is retired needlessly).
        if self.setup_timeout_seconds >= self.browser_operation_timeout_seconds:
            raise ValueError(
                "setup_timeout_seconds must be < browser_operation_timeout_seconds "
                f"({self.setup_timeout_seconds} >= {self.browser_operation_timeout_seconds})"
            )
        if self.reward_timeout_seconds >= self.browser_evaluation_timeout_seconds:
            raise ValueError(
                "reward_timeout_seconds must be < browser_evaluation_timeout_seconds "
                f"({self.reward_timeout_seconds} >= {self.browser_evaluation_timeout_seconds})"
            )
        return self


def task_info_from_row(task: WebArenaTaskRow) -> CuaGymTaskInfo:
    extra = getattr(task, "cuagym", None)
    if extra is None:
        extra = (task.model_extra or {}).get("cuagym")
    if extra is None:
        raise ValueError(f"task {task.task_id} has no `cuagym` field")
    if isinstance(extra, CuaGymTaskInfo):
        return extra
    return CuaGymTaskInfo.model_validate(extra)
