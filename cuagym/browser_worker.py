# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Ray browser actor for CUA-Gym-Hub episodes.

Mirrors ``resources_servers.webarena.browser_worker`` (one persistent
Xvfb + Chromium per actor, one episode at a time) with hub-specific
``reset``/``evaluate``:

- ``reset`` mints a fresh episode sid, fills it into the row's inlined
  setup program (``__CUA_GYM_SID__`` placeholder) alongside the hub
  endpoints, runs the program in a subprocess (source over stdin — nothing
  is written to disk), then navigates the pooled browser to the mock app
  with that sid;
- ``evaluate`` fills the same placeholders into the row's inlined reward
  program, runs it, and parses the printed ``REWARD:`` line.

The class is a copy rather than a subclass because ``@ray.remote`` classes do
not subclass cleanly; ``step`` and the Xvfb/Chromium lifecycle are identical
to the WebArena worker.
"""

from __future__ import annotations

import asyncio
import io
import logging
import os
import subprocess
import uuid
from typing import Any

import psutil
import ray
from PIL import ImageGrab

from resources_servers.cuagym.episode_code import (
    app_url,
    parse_reward,
    run_code,
    substitute,
    tail,
)
from resources_servers.cuagym.schemas import CuaGymResourcesServerConfig, task_info_from_row
from resources_servers.webarena.actions import (
    decode_tool_arguments,
    execute_computer_actions,
    validate_tool_arguments,
)
from resources_servers.webarena.browser import (
    CHROME_ARGS,
    _install_dialog_handler,
    tab_context,
)
from resources_servers.webarena.browser_worker import _start_xvfb, _stop_process_group
from resources_servers.webarena.schemas import WebArenaTaskRow


logger = logging.getLogger(__name__)

import time  # noqa: E402  (kept close to usage parity with the webarena worker)


def _browser_rss_snapshot() -> tuple[int, int, int]:
    """Return Chromium process count, summed RSS, and actor RSS in bytes."""
    actor = psutil.Process()
    chromium_count = 0
    chromium_rss = 0
    for process in actor.children(recursive=True):
        try:
            descriptor = " ".join((process.name(), *process.cmdline())).lower()
            if "chrome" not in descriptor and "chromium" not in descriptor:
                continue
            chromium_rss += process.memory_info().rss
            chromium_count += 1
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
            continue
    return chromium_count, chromium_rss, actor.memory_info().rss


async def _open_episode(
    browser: Any,
    start_url: str,
    *,
    viewport_width: int,
    viewport_height: int,
) -> tuple[Any, Any]:
    """Create the episode context/page inside the worker's event loop.

    Playwright's async API (page.on, task scheduling) requires a running
    loop, so everything from new_context to the first goto happens here.
    Module-level on purpose: an ``async def`` method on the actor class would
    make Ray treat the whole actor as an async actor and run its methods
    inside Ray's own event loop, breaking the run_until_complete pattern.
    """
    context = await browser.new_context(viewport={"width": viewport_width, "height": viewport_height})
    context.set_default_timeout(45_000)
    context.set_default_navigation_timeout(45_000)
    page = await context.new_page()
    _install_dialog_handler(page)
    await page.goto(start_url, wait_until="domcontentloaded")
    return context, page


@ray.remote(max_concurrency=1)
class CuaGymBrowserWorker:
    """One persistent Chromium/Xvfb process with at most one active episode."""

    def __init__(self, config: dict[str, Any]):
        self.config = CuaGymResourcesServerConfig.model_validate(config)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.xvfb_process: subprocess.Popen | None = None
        self.display: str | None = None
        self.playwright: Any | None = None
        self.browser: Any | None = None
        self.context: Any | None = None
        self.page: Any | None = None
        self.pyautogui: Any | None = None
        self.task: WebArenaTaskRow | None = None
        self.sid: str | None = None
        self.reward_code: str | None = None
        self._startup()

    def _startup(self) -> None:
        import os

        self.xvfb_process, self.display = _start_xvfb(
            self.config.viewport_width,
            self.config.viewport_height,
        )
        os.environ["DISPLAY"] = self.display
        os.environ.pop("WAYLAND_DISPLAY", None)
        try:
            import pyautogui
            from playwright.async_api import async_playwright

            pyautogui.FAILSAFE = False
            pyautogui.PAUSE = 0
            self.pyautogui = pyautogui
            self.playwright = self.loop.run_until_complete(async_playwright().start())
            self.browser = self.loop.run_until_complete(
                self.playwright.chromium.launch(
                    headless=False,
                    args=[
                        *CHROME_ARGS,
                        f"--window-size={self.config.viewport_width},{self.config.viewport_height}",
                    ],
                )
            )
        except Exception:
            self.shutdown()
            raise

    def health(self) -> dict[str, Any]:
        return {
            "healthy": bool(
                self.xvfb_process
                and self.xvfb_process.poll() is None
                and self.browser is not None
                and self.browser.is_connected()
            ),
            "display": self.display,
            "active": self.context is not None,
        }

    def reset(self, task_payload: dict[str, Any]) -> dict[str, Any]:
        self.close_episode()
        task = WebArenaTaskRow.model_validate(task_payload)
        info = task_info_from_row(task)

        # Resolve the app's port before running setup: an unknown app_dir must
        # fail before the program mutates hub state for an episode that could
        # never be opened.
        base_url = app_url(info.app_dir, self.config.hub_base_url, self.config.hub_base_port)

        sid = str(uuid.uuid4())
        if info.initial_setup:
            setup_code = substitute(
                info.initial_setup,
                sid=sid,
                hub_base_url=self.config.hub_base_url,
                base_port=self.config.hub_base_port,
            )
            result = run_code(setup_code, timeout_seconds=self.config.setup_timeout_seconds)
            if result.returncode != 0:
                raise RuntimeError(
                    f"initial_setup failed for task {info.bundle_id} "
                    f"(rc={result.returncode}): {tail(result.stdout)} {tail(result.stderr)}"
                )

        self.task = task
        self.sid = sid
        self.reward_code = info.eval_reward_code

        start_url = f"{base_url}/?sid={sid}"
        self.context, self.page = self.loop.run_until_complete(
            _open_episode(
                self.browser,
                start_url,
                viewport_width=self.config.viewport_width,
                viewport_height=self.config.viewport_height,
            )
        )
        time.sleep(self.config.post_action_screenshot_delay_seconds)

        return {
            "screenshot": self._screenshot(),
            "tab_context": self.loop.run_until_complete(tab_context(self.page)),
            "task": self.task.model_dump(mode="json"),
        }

    def step(self, tool_call: dict[str, Any]) -> dict[str, Any]:
        if self.context is None or self.page is None or self.task is None:
            raise RuntimeError("No CUA-Gym episode is active")
        name = str(tool_call["name"])
        call_id = str(tool_call["call_id"])
        done = False
        status = None
        answer = None
        function_output = None
        before_pages = len(self.context.pages)
        try:
            arguments = validate_tool_arguments(
                name,
                decode_tool_arguments(tool_call.get("arguments")),
            )
            if name == "navigate":
                self._select_page(arguments.get("tab_id"))
                url = arguments["url"]
                if url == "back":
                    self.loop.run_until_complete(self.page.go_back(wait_until="domcontentloaded"))
                elif url == "forward":
                    self.loop.run_until_complete(self.page.go_forward(wait_until="domcontentloaded"))
                else:
                    self.loop.run_until_complete(self.page.goto(url, wait_until="domcontentloaded"))
            elif name == "computer":
                self.loop.run_until_complete(self.page.bring_to_front())
                execute_computer_actions(
                    self.pyautogui,
                    arguments,
                    width=self.config.viewport_width,
                    height=self.config.viewport_height,
                )
                if len(self.context.pages) > before_pages:
                    self.page = self.context.pages[-1]
            elif name == "tabs_create":
                self.page = self.loop.run_until_complete(self.context.new_page())
                self.loop.run_until_complete(
                    self.page.goto(
                        arguments.get("url") or "about:blank",
                        wait_until="domcontentloaded",
                    )
                )
            elif name == "tabs_focus":
                self._select_page(arguments["tab_id"])
                self.loop.run_until_complete(self.page.bring_to_front())
            elif name == "terminate":
                done = True
                status = arguments["status"]
                answer = arguments.get("answer")
        except Exception as exc:
            logger.info(
                "Recoverable CUA-Gym tool error for %s: %s: %s",
                name,
                type(exc).__name__,
                exc,
            )
            function_output = f"Tool error: {type(exc).__name__}: {exc}"

        result: dict[str, Any] = {
            "call_id": call_id,
            "function_output": function_output,
            "done": done,
            "reward": 0.0,
            "termination_status": status,
            "answer": answer,
            "evaluator_details": {},
        }
        if not done:
            time.sleep(self.config.post_action_screenshot_delay_seconds)
            result.update(
                screenshot=self._screenshot(),
                tab_context=self.loop.run_until_complete(tab_context(self.page)),
            )
        return result

    def evaluate(self, *, status: str | None, answer: str | None) -> dict[str, Any]:
        if self.reward_code is None or self.sid is None:
            raise RuntimeError("No CUA-Gym episode is active")
        details: dict[str, Any] = {"sid": self.sid}
        reward = 0.0
        try:
            reward_code = substitute(
                self.reward_code,
                sid=self.sid,
                hub_base_url=self.config.hub_base_url,
                base_port=self.config.hub_base_port,
            )
            result = run_code(
                reward_code,
                timeout_seconds=self.config.reward_timeout_seconds,
                extra_env={
                    "CUA_GYM_AGENT_ANSWER": answer or "",
                    "CUA_GYM_AGENT_STATUS": status or "",
                },
            )
            parsed = parse_reward(result.stdout)
            details.update(
                returncode=result.returncode,
                stdout_tail=tail(result.stdout),
                stderr_tail=tail(result.stderr),
            )
            if parsed is None:
                details["message"] = "reward code produced no REWARD: line"
            else:
                reward = parsed
                details["message"] = f"reward code: score={parsed}"
        except subprocess.TimeoutExpired:
            details["message"] = f"reward code timed out after {self.config.reward_timeout_seconds}s"
        except Exception as exc:
            logger.exception("CUA-Gym reward execution failed")
            details["message"] = f"reward execution error: {type(exc).__name__}: {exc}"
        return {
            "reward": reward,
            "termination_status": status,
            "answer": answer,
            "evaluator_details": details,
        }

    def _select_page(self, tab_id: Any) -> None:
        if tab_id is None:
            return
        index = int(tab_id)
        pages = list(self.context.pages)
        if index < 0 or index >= len(pages):
            raise ValueError(f"tab_id={index} is outside [0, {len(pages) - 1}]")
        self.page = pages[index]

    def _screenshot(self) -> bytes:
        image = ImageGrab.grab(xdisplay=self.display)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        data = buffer.getvalue()
        # Opt-in rollout-visualization dump: set CUAGYM_SCREENSHOT_DUMP_DIR to
        # persist every observation as <dir>/<sid>/<seq>.png. Off by default.
        dump_dir = os.environ.get("CUAGYM_SCREENSHOT_DUMP_DIR")
        if dump_dir and self.sid:
            try:
                ep_dir = os.path.join(dump_dir, self.sid)
                os.makedirs(ep_dir, exist_ok=True)
                self._shot_seq = getattr(self, "_shot_seq", -1) + 1
                with open(os.path.join(ep_dir, f"{self._shot_seq:03d}.png"), "wb") as f:
                    f.write(data)
            except OSError:
                logging.getLogger(__name__).warning("screenshot dump failed", exc_info=True)
        return data

    def close_episode(self) -> bool:
        sid = self.sid
        before_count, before_chromium_rss, before_actor_rss = (
            _browser_rss_snapshot()
        )
        ok = True
        if self.context is not None:
            try:
                self.loop.run_until_complete(self.context.close())
            except Exception:
                logger.warning("Failed to close CUA-Gym browser context", exc_info=True)
                ok = False
            finally:
                self.context = None
                self.page = None
                self.task = None
                self.sid = None
                self.reward_code = None
        after_count, after_chromium_rss, after_actor_rss = _browser_rss_snapshot()
        mib = 1024**2
        logger.info(
            "CUA-Gym browser RSS after close_episode: "
            "sid=%s chromium_processes=%d->%d chromium_rss_mb=%.2f->%.2f "
            "chromium_delta_mb=%+.2f actor_rss_mb=%.2f->%.2f actor_delta_mb=%+.2f",
            sid,
            before_count,
            after_count,
            before_chromium_rss / mib,
            after_chromium_rss / mib,
            (after_chromium_rss - before_chromium_rss) / mib,
            before_actor_rss / mib,
            after_actor_rss / mib,
            (after_actor_rss - before_actor_rss) / mib,
        )
        return ok

    def shutdown(self) -> None:
        self.close_episode()
        if self.browser is not None:
            try:
                self.loop.run_until_complete(self.browser.close())
            except Exception:
                logger.debug("Failed to close Chromium", exc_info=True)
            self.browser = None
        if self.playwright is not None:
            try:
                self.loop.run_until_complete(self.playwright.stop())
            except Exception:
                logger.debug("Failed to stop Playwright", exc_info=True)
            self.playwright = None
        _stop_process_group(self.xvfb_process)
        self.xvfb_process = None
        if not self.loop.is_closed():
            self.loop.close()
