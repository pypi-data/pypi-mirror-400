from __future__ import annotations

import uuid

from .context import ToolContext
from .errors import error_response
from .policy import PolicyAction
from .utils import truncate_text, with_trace

try:
    from playwright.sync_api import sync_playwright
except Exception:  # pragma: no cover - optional dependency
    sync_playwright = None


class _BrowserStore:
    def __init__(self) -> None:
        self._playwright = None
        self._browser = None
        self._pages: dict[str, object] = {}

    def start(self) -> None:
        if sync_playwright is None:
            raise RuntimeError("playwright is not available")
        if self._playwright is None:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(headless=True)

    def new_page(self, viewport: dict | None):
        self.start()
        page = self._browser.new_page(viewport=viewport) if viewport else self._browser.new_page()
        page_id = uuid.uuid4().hex
        self._pages[page_id] = page
        return page_id, page

    def get_page(self, page_id: str):
        return self._pages.get(page_id)


_STORE = _BrowserStore()


def browser_open(
    url: str,
    viewport: dict | None = None,
    timeout_ms: int | None = None,
    *,
    context: ToolContext,
) -> dict:
    def run() -> dict:
        decision = context.policy.evaluate(PolicyAction(action_type="open_url", url=url))
        if not decision.allowed:
            return error_response("POLICY_DENIED", decision.reason)
        try:
            page_id, page = _STORE.new_page(viewport)
            page.goto(url, timeout=timeout_ms or 10000)
            return {"page_id": page_id, "final_url": page.url, "title": page.title()}
        except Exception as exc:
            return error_response("NETWORK_ERROR", str(exc))

    return with_trace(
        "browser_open",
        context.request_id,
        context.tracer,
        {"url": url, "timeout_ms": timeout_ms},
        run,
    )


def browser_act(
    page_id: str,
    actions: list[dict],
    timeout_ms: int | None = None,
    *,
    context: ToolContext,
) -> dict:
    def run() -> dict:
        if context.limits.max_actions is not None and len(actions) > context.limits.max_actions:
            return error_response("TOO_LARGE", "too many actions")
        page = _STORE.get_page(page_id)
        if page is None:
            return error_response("NOT_FOUND", f"page_id: {page_id}")
        logs: list[str] = []
        try:
            for idx, action in enumerate(actions):
                action_type = action.get("type")
                if action_type == "click":
                    page.click(action["selector"], timeout=timeout_ms or 10000)
                elif action_type == "fill":
                    page.fill(action["selector"], action.get("text", ""), timeout=timeout_ms or 10000)
                elif action_type == "press":
                    page.press(action["selector"], action.get("key", ""), timeout=timeout_ms or 10000)
                elif action_type == "wait_for":
                    wait_ms = action.get("timeout_ms", timeout_ms or 10000)
                    if context.limits.max_wait_ms is not None and wait_ms > context.limits.max_wait_ms:
                        return error_response("INVALID_ARGUMENT", "wait_for timeout exceeds limit")
                    selector = action.get("selector")
                    if selector:
                        page.wait_for_selector(selector, timeout=wait_ms)
                    else:
                        page.wait_for_timeout(wait_ms)
                elif action_type == "scroll":
                    page.evaluate("window.scrollBy(0, arguments[0])", action.get("y", 0))
                elif action_type == "select":
                    page.select_option(action["selector"], action.get("value"))
                else:
                    return error_response("INVALID_ARGUMENT", f"unknown action: {action_type}")
                logs.append(f"ok:{idx}:{action_type}")
        except Exception as exc:
            logs.append(f"error:{idx}:{action_type}:{exc}")
            logs_text = "\n".join(logs)
            logs_text, truncated = truncate_text(logs_text, context.limits.max_output_chars)
            error_payload = error_response("INTERNAL_ERROR", f"action {idx} {action_type}: {exc}", truncated=truncated)
            error_payload["logs"] = logs_text.splitlines()
            return error_payload
        logs_text = "\n".join(logs)
        logs_text, truncated = truncate_text(logs_text, context.limits.max_output_chars)
        return {"ok": True, "logs": logs_text.splitlines(), "truncated": truncated}

    return with_trace(
        "browser_act",
        context.request_id,
        context.tracer,
        {"page_id": page_id, "actions": len(actions), "timeout_ms": timeout_ms},
        run,
    )


def browser_extract(
    page_id: str,
    selectors: list[str] | None = None,
    extract: list[str] | None = None,
    *,
    context: ToolContext,
) -> dict:
    def run() -> dict:
        page = _STORE.get_page(page_id)
        if page is None:
            return error_response("NOT_FOUND", f"page_id: {page_id}")
        want = extract or ["text"]
        result: dict[str, object] = {}
        truncated = False
        try:
            if "text" in want:
                if selectors:
                    parts = [page.inner_text(sel) for sel in selectors]
                    text = "\n".join(parts)
                else:
                    text = page.inner_text("body")
                text, text_truncated = truncate_text(text, context.limits.max_output_chars)
                result["text"] = text
                truncated = truncated or text_truncated
            if "links" in want:
                links = page.eval_on_selector_all("a", "els => els.map(e => ({text: e.textContent, url: e.href}))")
                max_items = context.limits.max_matches
                if max_items is not None and len(links) > max_items:
                    links = links[:max_items]
                    truncated = True
                result["links"] = links
            if "tables" in want:
                tables = page.eval_on_selector_all(
                    "table",
                    "els => els.map(t => Array.from(t.rows).map(r => Array.from(r.cells).map(c => c.textContent)))",
                )
                max_items = context.limits.max_matches
                if max_items is not None and len(tables) > max_items:
                    tables = tables[:max_items]
                    truncated = True
                if max_items is not None:
                    trimmed_tables = []
                    for table in tables:
                        if len(table) > max_items:
                            table = table[:max_items]
                            truncated = True
                        trimmed_rows = []
                        for row in table:
                            if len(row) > max_items:
                                row = row[:max_items]
                                truncated = True
                            trimmed_rows.append(row)
                        trimmed_tables.append(trimmed_rows)
                    tables = trimmed_tables
                result["tables"] = tables
        except Exception as exc:
            return error_response("INTERNAL_ERROR", str(exc))
        result["truncated"] = truncated
        return result

    return with_trace(
        "browser_extract",
        context.request_id,
        context.tracer,
        {"page_id": page_id, "selectors": selectors, "extract": extract},
        run,
    )
