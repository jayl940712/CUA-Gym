"""Collect immutable browser/state evidence before running ``reward.py``."""

from __future__ import annotations

import ast
import inspect
import json
import re
from dataclasses import dataclass
from typing import Any, Callable
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from playwright.async_api import Page

from .models import WebTaskManifest
from .registry import Endpoint
from .state import SessionHandle, with_sid

PLACEHOLDER_RE = re.compile(r"__([A-Z0-9_]+)__")
Helper = Callable[..., Any]


def _route(url: str) -> str:
    parsed = urlsplit(url)
    query = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key != "sid"
    ]
    path = parsed.path or "/"
    if path != "/":
        path = path.rstrip("/")
    return urlunsplit(("", "", path, urlencode(sorted(query)), ""))


def _source_from_reference(reference: str) -> str | None:
    match = PLACEHOLDER_RE.search(reference)
    return match.group(1).lower() if match else None


def _path_from_reference(reference: str) -> str:
    value = PLACEHOLDER_RE.sub("", reference, count=1)
    parsed = urlsplit(value)
    if parsed.scheme and parsed.netloc:
        return urlunsplit(("", "", parsed.path or "/", parsed.query, parsed.fragment))
    if not value:
        return "/"
    return value if value.startswith("/") else f"/{value}"


def _reddit_post_url(url: str) -> str:
    parsed = urlsplit(url)
    tokens = parsed.path.split("/")
    if len(tokens) < 4 or tokens[1] != "f":
        return url
    return urlunsplit(
        (parsed.scheme, parsed.netloc, f"/f/{tokens[2]}/{tokens[3]}/", "", "")
    )


@dataclass
class BrowserEvidence:
    """Live browser handles used only while collecting immutable observations."""

    pages: dict[str, Page]
    endpoints: dict[str, Endpoint]
    sessions: dict[str, SessionHandle]
    active_source: str
    current_states: dict[str, dict[str, Any]] | None = None

    def active_page(self) -> Page:
        try:
            return self.pages[self.active_source]
        except KeyError as exc:
            raise ValueError(f"no active page for {self.active_source!r}") from exc

    async def page_for_reference(self, reference: str) -> Page:
        if reference in {"", "last"}:
            return self.active_page()
        source = _source_from_reference(reference) or self.active_source
        if source not in self.pages:
            raise ValueError(f"evidence references unavailable site {source!r}")
        page = self.pages[source]
        endpoint = self.endpoints[source]
        session = self.sessions[source]
        target = with_sid(
            f"{endpoint.base_url}{_path_from_reference(reference)}",
            session.browser_sid,
        )
        if _route(page.url) != _route(target):
            await page.goto(target, wait_until="domcontentloaded")
        return page

    def open_pages(self) -> list[Page]:
        pages: list[Page] = []
        for page in self.pages.values():
            context = getattr(page, "context", None)
            for candidate in getattr(context, "pages", [page]):
                is_closed = getattr(candidate, "is_closed", None)
                if candidate not in pages and not (is_closed and is_closed()):
                    pages.append(candidate)
        return pages or list(self.pages.values())


class EvidenceCollector:
    """Observe browser outcomes without assigning any reward."""

    def __init__(self, helpers: dict[str, Helper] | None = None) -> None:
        self.helpers = helpers or {}

    async def collect(
        self,
        task: WebTaskManifest,
        browser: BrowserEvidence,
        snapshots: dict[str, dict[str, Any]],
        lane_name: str,
    ) -> dict[str, Any]:
        apps: dict[str, Any] = {}
        open_pages = browser.open_pages()
        for source, page in browser.pages.items():
            endpoint_host = urlsplit(browser.endpoints[source].base_url).netloc
            source_pages = [
                candidate
                for candidate in open_pages
                if urlsplit(candidate.url).netloc == endpoint_host
            ] or [page]
            snapshot = snapshots[source]
            apps[source] = {
                "initial_state": snapshot.get("initial_state", {}),
                "current_state": snapshot.get("current_state", {}),
                "state_diff": snapshot.get("state_diff", {}),
                "final_urls": [candidate.url for candidate in source_pages],
                "final_html": await page.content(),
                "final_text": await page.locator("body").inner_text(),
            }

        observations: list[dict[str, Any]] = []
        for request in task.evidence:
            observations.extend(await self._collect_request(request, browser))

        return {
            "schema_version": 1,
            "task_id": task.task_id,
            "instruction": task.instruction,
            "lane": lane_name,
            "apps": apps,
            "observations": observations,
        }

    async def _collect_request(
        self, request: dict[str, Any], browser: BrowserEvidence
    ) -> list[dict[str, Any]]:
        target = str(request.get("url") or "last")
        candidates = (
            browser.open_pages() if target == "last" else [browser.active_page()]
        )
        observations = []
        for candidate in candidates:
            observation = {
                "name": request.get("name"),
                "index": request.get("index"),
                "url": target,
                "locator": request.get("locator", ""),
                "page_url": candidate.url,
            }
            try:
                observation["content"] = await self._observe(
                    request, candidate, browser
                )
            except Exception as exc:
                observation["content"] = ""
                observation["error"] = f"{type(exc).__name__}: {exc}"
            observations.append(observation)
        return observations

    async def _observe(
        self,
        request: dict[str, Any],
        candidate: Page,
        browser: BrowserEvidence,
    ) -> str:
        target = str(request.get("url") or "last")
        if target.startswith("func:"):
            target = str(await self._eval_helper(target, candidate, browser))
        page = candidate if target == "last" else await browser.page_for_reference(target)
        locator = str(request.get("locator") or "").strip()
        if locator.startswith(("document.", "[...document.", "() =>")):
            for action in request.get("prep_actions", []):
                try:
                    await page.evaluate(f"() => {action}")
                except Exception:
                    pass
            expression = locator if locator.startswith("() =>") else f"() => {locator}"
            return str(await page.evaluate(expression) or "")
        if locator.startswith("func:"):
            return str(await self._eval_helper(locator, page, browser))
        if locator:
            nodes = page.locator(locator)
            if await nodes.count() == 0:
                raise ValueError(f"locator selected no nodes: {locator}")
            return "\n".join(await nodes.all_inner_texts())
        return await page.content()

    async def _eval_helper(
        self, expression: str, page: Page, browser: BrowserEvidence
    ) -> Any:
        source = expression.removeprefix("func:").replace(
            "__last_url__", repr(str(page.url))
        )
        call = ast.parse(source, mode="eval").body
        if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name):
            raise ValueError(f"unsupported evidence helper: {expression}")
        args = [
            page
            if isinstance(argument, ast.Name) and argument.id == "__page__"
            else ast.literal_eval(argument)
            for argument in call.args
        ]
        helper = self.helpers.get(call.func.id)
        if helper is not None:
            result = helper(*args)
            return await result if inspect.isawaitable(result) else result
        return await self._default_helper(call.func.id, args, page, browser)

    async def _default_helper(
        self,
        name: str,
        args: list[Any],
        page: Page,
        browser: BrowserEvidence,
    ) -> Any:
        states = browser.current_states or {}
        if name == "reddit_get_post_url":
            return _reddit_post_url(str(args[0]))
        if name in {"get_query_text", "get_query_text_lowercase"}:
            value = await page.locator(str(args[-1])).inner_text()
            return value.lower() if name.endswith("_lowercase") else value
        if name == "gitlab_get_project_memeber_role":
            account = str(args[-1])
            index = await page.evaluate(
                """
                account => [...document.querySelectorAll(
                  "td[data-label='Account'] span.gl-avatar-labeled-sublabel"
                )].findIndex(node => node.innerText === `@${account}`)
                """,
                account,
            )
            return await page.evaluate(
                'index => document.querySelectorAll("td.col-max-role span")'
                '[index]?.innerText || ""',
                index,
            )
        if name == "shopping_get_latest_order_url":
            state = states.get("shopping", {})
            orders = state.get("orders") or []
            order_id = state.get("lastPlacedOrderId")
            order = next(
                (
                    item
                    for item in orders
                    if str(item.get("entityId") or item.get("entity_id"))
                    == str(order_id)
                ),
                orders[0] if orders else None,
            )
            if not order:
                return ""
            increment = order.get("incrementId") or order.get("increment_id")
            return (
                f"{browser.endpoints['shopping'].base_url}"
                f"/sales/order/view/order_id/{int(increment)}/"
            )
        if name.startswith("shopping_get_sku_latest_review_"):
            reviews = states.get("shopping", {}).get("myReviews") or []
            if not reviews:
                return ""
            review = reviews[-1]
            if name.endswith("_author"):
                return str(review.get("nickname") or "")
            if name.endswith("_rating"):
                return str((review.get("rating") or 0) * 20)
        if name == "shopping_admin_get_cart_price_rule":
            requested = str(args[0]).casefold()
            rules = states.get("shopping_admin", {}).get("cartPriceRules") or []
            rule = next(
                (
                    item
                    for item in rules
                    if str(item.get("name") or "").casefold() == requested
                ),
                None,
            )
            if not rule:
                return ""
            normalized = {
                "name": rule.get("name"),
                "customer_group_ids": rule.get("customer_group_ids"),
                "simple_action": rule.get("simple_action"),
                "discount_amount": str(rule.get("discount_amount") or "")
                .rstrip("0")
                .rstrip("."),
            }
            return json.dumps(normalized, ensure_ascii=True, sort_keys=True)
        raise ValueError(f"unsupported evidence helper: {name}")
