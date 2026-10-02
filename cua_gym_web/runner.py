"""Isolated Playwright execution for imported WebArena tasks."""

from __future__ import annotations

import asyncio
import importlib.util
import inspect
import json
import re
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Awaitable, Callable

from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright

from .evidence import BrowserEvidence, EvidenceCollector
from .models import AppSpec, EvaluationResult, WebTaskManifest
from .registry import Endpoint, EndpointRegistry
from .reward import PythonRewardRunner
from .state import SessionHandle, SessionMode, StateApiError, StateClient, with_sid

ReplayCallable = Callable[["BrowserLane", WebTaskManifest], Any | Awaitable[Any]]


def _sid(task_id: str, lane: str, run_id: str) -> str:
    prefix = re.sub(r"[^A-Za-z0-9_-]", "_", task_id).strip("_") or "task"
    suffix = f"_{lane}_{run_id}"
    return f"{prefix[:128 - len(suffix)]}{suffix}"


def _load_json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object in {path}")
    return value


def load_replay(path: str | Path) -> ReplayCallable:
    replay_path = Path(path).resolve()
    spec = importlib.util.spec_from_file_location(
        f"cua_gym_replay_{replay_path.stem}_{uuid.uuid4().hex}", replay_path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load replay module: {replay_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    callback = getattr(module, "run", None)
    if not callable(callback):
        raise TypeError(f"{replay_path} must define callable run(lane, task)")
    return callback


@dataclass
class BrowserLane:
    name: str
    sid: str
    context: BrowserContext
    pages: dict[str, Page]
    endpoints: dict[str, Endpoint]
    sessions: dict[str, SessionHandle]
    active_source: str
    browser_errors: list[str] = field(default_factory=list)
    # Set only on the replay lane, from the replay's return value. The initial
    # lane never runs a replay, so it stays None -> "" in the evidence document,
    # which is what keeps an answer-scored reward at 0.0 on the initial lane.
    answer: str | None = None

    def page(self, source_name: str | None = None) -> Page:
        return self.pages[source_name or self.active_source]

    def evidence(
        self, current_states: dict[str, dict[str, Any]] | None = None
    ) -> BrowserEvidence:
        return BrowserEvidence(
            pages=self.pages,
            endpoints=self.endpoints,
            sessions=self.sessions,
            active_source=self.active_source,
            current_states=current_states,
        )


class WebTaskRunner:
    """Run no-op, oracle, and Playwright replay lanes without VMs."""

    def __init__(
        self,
        task: WebTaskManifest,
        registry: EndpointRegistry,
        task_dir: str | Path,
        output_dir: str | Path,
        *,
        mode: SessionMode = SessionMode.LEGACY,
        admin_token: str | None = None,
        headless: bool = True,
        browser_executable: str | None = None,
        reward_runner: PythonRewardRunner | None = None,
    ) -> None:
        self.task = task
        self.registry = registry
        self.task_dir = Path(task_dir)
        self.output_dir = Path(output_dir)
        self.mode = mode
        self.admin_token = admin_token
        self.headless = headless
        self.browser_executable = browser_executable
        self.reward_runner = reward_runner or PythonRewardRunner()
        self.evidence_collector = EvidenceCollector()
        self.run_id = uuid.uuid4().hex[:12]

    async def run(self, replay: ReplayCallable | None = None) -> dict[str, Any]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        async with async_playwright() as playwright:
            request = await playwright.request.new_context()
            browser = await playwright.chromium.launch(
                headless=self.headless,
                executable_path=self.browser_executable,
            )
            try:
                return await self._run(playwright, browser, request, replay)
            finally:
                await browser.close()
                await request.dispose()

    async def _run(
        self,
        playwright: Playwright,
        browser: Browser,
        request: Any,
        replay: ReplayCallable | None,
    ) -> dict[str, Any]:
        del playwright  # kept in the signature to make ownership explicit
        endpoints = {
            app.source_name: self.registry.resolve(app) for app in self.task.apps
        }
        # Only stateful apps get a StateClient. Every `for source, client in
        # clients.items()` loop below then skips stateless apps for free, which
        # is what stops a /go?sid= call from raising StateApiError against a
        # deployment that has no such endpoint (OSM returns 404 there).
        stateful = {app.source_name for app in self.task.apps if not app.stateless}
        clients = {
            source: StateClient(
                request,
                endpoint,
                mode=self.mode,
                admin_token=self.admin_token,
            )
            for source, endpoint in endpoints.items()
            if source in stateful
        }
        initial_states = await self._initial_states(clients)
        lanes: list[BrowserLane] = []
        cleanup_sids: set[str] = set()
        report: dict[str, Any] = {
            "schema_version": 1,
            "task_id": self.task.task_id,
            "run_id": self.run_id,
            "mode": self.mode.value,
            "lanes": {},
        }

        try:
            cleanup_sids.add(_sid(self.task.task_id, "initial", self.run_id))
            initial = await self._open_lane(
                browser, "initial", initial_states, endpoints, clients
            )
            lanes.append(initial)
            initial_result, _ = await self._evaluate_lane(initial, clients)
            await self._capture_lane(initial, clients)
            report["lanes"]["initial"] = await self._lane_report(
                initial, clients, initial_result
            )

            if any(app.golden_state for app in self.task.apps):
                cleanup_sids.add(_sid(self.task.task_id, "oracle", self.run_id))
            oracle = await self._maybe_oracle(
                browser, initial_states, endpoints, clients
            )
            if oracle is not None:
                lanes.append(oracle)
                oracle_result, _ = await self._evaluate_lane(oracle, clients)
                await self._capture_lane(oracle, clients)
                report["lanes"]["oracle"] = await self._lane_report(
                    oracle, clients, oracle_result
                )

            if replay is not None:
                cleanup_sids.add(_sid(self.task.task_id, "replay", self.run_id))
                replay_lane = await self._open_lane(
                    browser, "replay", initial_states, endpoints, clients, trace=True
                )
                lanes.append(replay_lane)
                result = replay(replay_lane, self.task)
                if inspect.isawaitable(result):
                    result = await result
                # A replay may report an answer, mirroring the agent's
                # terminate(status, answer) at rollout time. Existing replays
                # return None, so this is a no-op for every task written so far.
                if isinstance(result, str):
                    replay_lane.answer = result
                elif isinstance(result, dict) and isinstance(result.get("answer"), str):
                    replay_lane.answer = result["answer"]
                await self._drain_writes(replay_lane, clients)
                replay_result, _ = await self._evaluate_lane(replay_lane, clients)
                await self._capture_lane(replay_lane, clients)
                await replay_lane.context.tracing.stop(
                    path=self.output_dir / "replay-trace.zip"
                )
                report["lanes"]["replay"] = await self._lane_report(
                    replay_lane, clients, replay_result
                )

            report["verification"] = self._verification(report)
            (self.output_dir / "verification.json").write_text(
                json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            return report
        finally:
            for lane in reversed(lanes):
                try:
                    await lane.context.close()
                except Exception:
                    pass
            for sid in cleanup_sids:
                for client in clients.values():
                    try:
                        await client.reset(sid)
                    except Exception:
                        pass

    async def _initial_states(
        self, clients: dict[str, StateClient]
    ) -> dict[str, dict[str, Any]]:
        states: dict[str, dict[str, Any]] = {}
        for app in self.task.apps:
            if app.stateless:
                continue
            if app.initial_state:
                states[app.source_name] = _load_json_object(
                    self.task_dir / app.initial_state
                )
            else:
                probe_sid = _sid(self.task.task_id, "probe", uuid.uuid4().hex[:12])
                states[app.source_name] = await clients[
                    app.source_name
                ].canonical_default(probe_sid)
        return states

    async def _open_lane(
        self,
        browser: Browser,
        name: str,
        states: dict[str, dict[str, Any]],
        endpoints: dict[str, Endpoint],
        clients: dict[str, StateClient],
        *,
        trace: bool = False,
    ) -> BrowserLane:
        sid = _sid(self.task.task_id, name, self.run_id)
        sessions: dict[str, SessionHandle] = {}
        setup_script = self.task_dir / "initial_setup.py"
        use_setup_script = setup_script.is_file()
        if use_setup_script:
            if self.mode is not SessionMode.LEGACY:
                raise ValueError(
                    "task_dir/initial_setup.py setup scripts only support legacy mode"
                )
            for app in self.task.apps:
                source = app.source_name
                await self._run_initial_setup(setup_script, app, sid, endpoints[source])
                snapshot = await clients[source].go(sid)
                initial = snapshot.get("initial_state")
                current = snapshot.get("current_state")
                if not isinstance(initial, dict) or initial != current:
                    raise StateApiError(
                        f"{source}: initial_setup.py did not establish equal "
                        "initial and current state"
                    )
                if snapshot.get("state_diff"):
                    raise StateApiError(
                        f"{source}: initial_setup.py left a non-empty state diff"
                    )
                sessions[source] = SessionHandle(
                    mock_name=endpoints[source].mock_name,
                    base_url=endpoints[source].base_url,
                    sid=sid,
                    mode=SessionMode.LEGACY,
                )
        else:
            for source, state in states.items():
                sessions[source], _ = await clients[source].establish(sid, state)

        # Stateless apps establish nothing; they still need a handle so the
        # navigation block below can look one up.
        for app in self.task.apps:
            if app.stateless and app.source_name not in sessions:
                sessions[app.source_name] = SessionHandle(
                    mock_name=endpoints[app.source_name].mock_name,
                    base_url=endpoints[app.source_name].base_url,
                    sid="",
                    mode=SessionMode.LEGACY,
                )

        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        try:
            if trace:
                await context.tracing.start(
                    screenshots=True, snapshots=True, sources=True
                )
            errors: list[str] = []
            pages: dict[str, Page] = {}
            for app in self.task.apps:
                page = await context.new_page()
                page.on(
                    "pageerror",
                    lambda error, source=app.source_name: errors.append(
                        f"{source}: {error}"
                    ),
                )
                page.on(
                    "console",
                    lambda message, source=app.source_name: (
                        errors.append(f"{source} console: {message.text}")
                        if message.type == "error"
                        else None
                    ),
                )
                session = sessions[app.source_name]
                if session.mode is SessionMode.HARDENED:
                    launch_url = session.launch_url or ""
                    if launch_url and not launch_url.lower().startswith(
                        ("http://", "https://")
                    ):
                        launch_url = f"{endpoints[app.source_name].base_url}{launch_url}"
                    await page.goto(launch_url, wait_until="domcontentloaded")
                base_target = f"{endpoints[app.source_name].base_url}{app.start_path}"
                target = (
                    base_target
                    if app.stateless
                    else with_sid(base_target, session.browser_sid)
                )
                await page.goto(target, wait_until="domcontentloaded")
                pages[app.source_name] = page
            return BrowserLane(
                name=name,
                sid=sid,
                context=context,
                pages=pages,
                endpoints=endpoints,
                sessions=sessions,
                active_source=self.task.apps[0].source_name,
                browser_errors=errors,
            )
        except Exception:
            await context.close()
            raise

    async def _run_initial_setup(
        self,
        script_path: Path,
        app: AppSpec,
        sid: str,
        endpoint: Endpoint,
    ) -> None:
        """Run a task bundle's optional ``initial_setup.py`` against one lane.

        The script talks to the mock's own state API (``/post``, ``/go``)
        exactly as it would under the NeMo-Gym runtime — it is executed as a
        standalone subprocess, never imported, and never touches the browser.
        Only the two placeholders it declares (``__CUA_GYM_SID__`` and its
        app's ``__<base_url_env>__``) are substituted; anything else left
        unresolved is a hard error rather than a silently wrong endpoint.
        """
        code = script_path.read_text(encoding="utf-8")
        code = code.replace("__CUA_GYM_SID__", sid)
        code = code.replace(f"__{app.base_url_env}__", endpoint.base_url)
        if "__CUA_GYM_" in code:
            raise ValueError(
                f"{app.source_name}: initial_setup.py has unresolved __CUA_GYM_*__ "
                "placeholders"
            )
        proc = await asyncio.create_subprocess_exec(
            sys.executable,
            "-c",
            code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.communicate()
            raise RuntimeError(f"{app.source_name}: initial_setup.py timed out")
        if proc.returncode != 0 or (
            b"SETUP OK" not in stdout and b"SETUP_OK" not in stdout
        ):
            raise RuntimeError(
                f"{app.source_name}: initial_setup.py failed (exit={proc.returncode})\n"
                f"stdout: {stdout.decode(errors='replace')[:2000]}\n"
                f"stderr: {stderr.decode(errors='replace')[:2000]}"
            )

    async def _maybe_oracle(
        self,
        browser: Browser,
        initial_states: dict[str, dict[str, Any]],
        endpoints: dict[str, Endpoint],
        clients: dict[str, StateClient],
    ) -> BrowserLane | None:
        if not any(app.golden_state for app in self.task.apps):
            return None
        if any(not app.golden_state for app in self.task.apps):
            raise ValueError("oracle lane requires golden_state for every participating app")
        lane = await self._open_lane(
            browser, "oracle", initial_states, endpoints, clients
        )
        for app in self.task.apps:
            golden = _load_json_object(self.task_dir / str(app.golden_state))
            await clients[app.source_name].set_current(lane.sid, golden)
        for page in lane.pages.values():
            await page.reload(wait_until="domcontentloaded")
        return lane

    async def _drain_writes(
        self,
        lane: BrowserLane,
        clients: dict[str, StateClient],
        timeout_seconds: float = 10.0,
    ) -> None:
        """Wait for browser writes without depending on Vite-only module imports."""
        for page in lane.pages.values():
            await page.wait_for_timeout(500)
        deadline = asyncio.get_running_loop().time() + timeout_seconds
        previous: dict[str, str] | None = None
        stable_reads = 0
        while asyncio.get_running_loop().time() < deadline:
            current = {
                source: json.dumps(
                    (await client.go(lane.sid)).get("current_state"),
                    sort_keys=True,
                    separators=(",", ":"),
                )
                for source, client in clients.items()
            }
            if current == previous:
                stable_reads += 1
                if stable_reads >= 2:
                    return
            else:
                stable_reads = 0
                previous = current
            await asyncio.sleep(0.25)
        raise TimeoutError("browser-backed state did not become stable before evaluation")

    async def _capture_lane(
        self, lane: BrowserLane, clients: dict[str, StateClient]
    ) -> None:
        screenshots = self.output_dir / "screenshots"
        screenshots.mkdir(parents=True, exist_ok=True)
        for source, page in lane.pages.items():
            await page.screenshot(
                path=screenshots / f"{lane.name}-{source}.png", full_page=True
            )
        states = {
            source: await client.go(lane.sid) for source, client in clients.items()
        }
        (self.output_dir / f"{lane.name}-states.json").write_text(
            json.dumps(states, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    async def _evaluate_lane(
        self,
        lane: BrowserLane,
        clients: dict[str, StateClient],
    ) -> tuple[EvaluationResult, dict[str, Any]]:
        snapshots: dict[str, dict[str, Any]] = {
            source: await client.go(lane.sid)
            for source, client in clients.items()
        }
        # A stateless app has no /go?sid=; its evidence carries empty state so
        # rewards fall back to final_urls / final_text / agent_answer.
        for app in self.task.apps:
            snapshots.setdefault(
                app.source_name,
                {"initial_state": {}, "current_state": {}, "state_diff": {}},
            )
        browser = lane.evidence(
            {
                source: snapshot.get("current_state", {})
                for source, snapshot in snapshots.items()
            }
        )
        immutable = await self.evidence_collector.collect(
            self.task, browser, snapshots, lane.name, answer=lane.answer
        )
        (self.output_dir / f"{lane.name}-evidence.json").write_text(
            json.dumps(immutable, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        result = await self.reward_runner.evaluate(
            self.task_dir / self.task.reward_path,
            immutable,
            (
                self.task_dir / self.task.requirements_path
                if self.task.requirements_path
                else None
            ),
        )
        return result, immutable

    async def _lane_report(
        self,
        lane: BrowserLane,
        clients: dict[str, StateClient],
        result: EvaluationResult,
    ) -> dict[str, Any]:
        return {
            "sid": lane.sid,
            "final_urls": {
                source: page.url for source, page in lane.pages.items()
            },
            "browser_errors": lane.browser_errors,
            "reward": result.to_dict(),
            "state_diffs": {
                source: (await client.go(lane.sid)).get("state_diff", {})
                for source, client in clients.items()
            },
        }

    @staticmethod
    def _verification(report: dict[str, Any]) -> dict[str, Any]:
        lanes = report["lanes"]
        initial_score = lanes["initial"]["reward"]["score"]
        gates = {
            "initial_scores_zero": initial_score == 0.0,
            "initial_has_no_browser_errors": not lanes["initial"]["browser_errors"],
        }
        if "oracle" in lanes:
            gates["oracle_passes"] = lanes["oracle"]["reward"]["score"] == 1.0
            gates["oracle_has_no_browser_errors"] = not lanes["oracle"]["browser_errors"]
        if "replay" in lanes:
            gates["replay_passes"] = lanes["replay"]["reward"]["score"] == 1.0
            gates["replay_has_no_browser_errors"] = not lanes["replay"]["browser_errors"]
        return {"passed": all(gates.values()), "gates": gates}
