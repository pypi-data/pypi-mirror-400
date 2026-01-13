from __future__ import annotations

import html
import os
import re
import urllib.request
from urllib.parse import urlparse

from .context import ToolContext
from .errors import error_response
from .policy import PolicyAction
from .utils import truncate_text, with_trace


def web_search(
    query: str,
    max_results: int | None = None,
    recency: str | None = None,
    domains_allow: list[str] | None = None,
    domains_block: list[str] | None = None,
    *,
    context: ToolContext,
) -> dict:
    def run() -> dict:
        provider = (context.policy.config.search_provider or "auto").lower()
        if provider not in {"auto", "tavily", "duckduckgo"}:
            return error_response("INVALID_ARGUMENT", f"unknown search provider: {provider}")
        tavily_key = os.getenv("TAVILY_API_KEY")
        if provider in {"auto", "tavily"} and tavily_key:
            try:
                from tavily import TavilyClient
            except Exception:
                return error_response("INTERNAL_ERROR", "tavily client is not available")
            limit = _resolve_limit(max_results, context.limits.max_matches)
            try:
                client = TavilyClient(api_key=tavily_key)
                response = client.search(query=query, max_results=limit or 10)
                results = []
                for item in response.get("results", []):
                    url = item.get("url")
                    if not url:
                        continue
                    if domains_allow and _host(url) not in domains_allow:
                        continue
                    if domains_block and _host(url) in domains_block:
                        continue
                    results.append(
                        {
                            "title": item.get("title"),
                            "url": url,
                            "snippet": item.get("content"),
                            "source": "tavily",
                            "published_at": item.get("published_date"),
                        }
                    )
                    if limit is not None and len(results) >= limit:
                        return {"results": results, "truncated": True}
                return {"results": results, "truncated": False}
            except Exception as exc:
                return error_response("NETWORK_ERROR", str(exc))
        if provider == "tavily" and not tavily_key:
            return error_response("INVALID_ARGUMENT", "TAVILY_API_KEY is not set")
        try:
            from duckduckgo_search import DDGS
        except Exception:
            return error_response("INTERNAL_ERROR", "search provider is not available")
        limit = _resolve_limit(max_results, context.limits.max_matches)
        results: list[dict] = []
        try:
            with DDGS() as ddgs:
                for item in ddgs.text(query, max_results=limit or 10):
                    url = item.get("href") or item.get("url")
                    if not url:
                        continue
                    if domains_allow and _host(url) not in domains_allow:
                        continue
                    if domains_block and _host(url) in domains_block:
                        continue
                    results.append(
                        {
                            "title": item.get("title"),
                            "url": url,
                            "snippet": item.get("body") or item.get("snippet"),
                            "source": item.get("source"),
                            "published_at": item.get("published"),
                        }
                    )
                    if limit is not None and len(results) >= limit:
                        return {"results": results, "truncated": True}
        except Exception as exc:
            return error_response("NETWORK_ERROR", str(exc))
        return {"results": results, "truncated": False}

    return with_trace(
        "web_search",
        context.request_id,
        context.tracer,
        {"query": query, "max_results": max_results, "recency": recency},
        run,
    )


def web_fetch(
    url: str,
    headers: dict | None = None,
    method: str = "GET",
    timeout_ms: int | None = None,
    *,
    context: ToolContext,
) -> dict:
    def run() -> dict:
        decision = context.policy.evaluate(PolicyAction(action_type="fetch_url", url=url))
        if not decision.allowed:
            return error_response("POLICY_DENIED", decision.reason)
        if method not in {"GET", "POST"}:
            return error_response("INVALID_ARGUMENT", f"unsupported method: {method}")
        req = urllib.request.Request(url=url, method=method, headers=headers or {})
        timeout = (timeout_ms or 10000) / 1000
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status = resp.status
                final_url = resp.geturl()
                content_type = resp.headers.get("Content-Type")
                limit = context.limits.max_fetch_bytes
                body_bytes = resp.read() if limit is None else resp.read(limit + 1)
        except Exception as exc:
            return error_response("NETWORK_ERROR", str(exc))
        if context.limits.max_fetch_bytes is not None and len(body_bytes) > context.limits.max_fetch_bytes:
            return error_response("TOO_LARGE", "fetch size exceeds limit")
        truncated = False
        encoding = _encoding_from_type(content_type) or "utf-8"
        body_text = body_bytes.decode(encoding, errors="replace")
        body_text, text_truncated = truncate_text(body_text, context.limits.max_output_chars)
        truncated = truncated or text_truncated
        return {
            "status": status,
            "final_url": final_url,
            "content_type": content_type,
            "body": body_text,
            "bytes": len(body_bytes),
            "truncated": truncated,
        }

    return with_trace(
        "web_fetch",
        context.request_id,
        context.tracer,
        {"url": url, "method": method, "timeout_ms": timeout_ms},
        run,
    )


def web_extract(
    html: str,
    mode: str = "markdown",
    max_chars: int | None = None,
    *,
    context: ToolContext,
) -> dict:
    def run() -> dict:
        if mode not in {"text", "markdown"}:
            return error_response("INVALID_ARGUMENT", f"unknown mode: {mode}")
        text = _extract_text(html)
        limit = _resolve_limit(max_chars, context.limits.max_output_chars)
        text, truncated = truncate_text(text, limit)
        return {"text": text, "markdown": text if mode == "markdown" else None, "truncated": truncated}

    return with_trace(
        "web_extract",
        context.request_id,
        context.tracer,
        {"mode": mode, "max_chars": max_chars, "size": len(html)},
        run,
    )


def _extract_text(html_text: str) -> str:
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html_text, "html.parser")
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text("\n")
        return _cleanup_text(text)
    except Exception:
        return _fallback_strip(html_text)


def _fallback_strip(html_text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html_text)
    return _cleanup_text(html.unescape(text))


def _cleanup_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join([line for line in lines if line])


def _encoding_from_type(content_type: str | None) -> str | None:
    if not content_type:
        return None
    parts = content_type.split(";")
    for part in parts[1:]:
        part = part.strip()
        if part.startswith("charset="):
            return part.split("=", 1)[1]
    return None


def _resolve_limit(primary: int | None, fallback: int | None) -> int | None:
    if primary is None:
        return fallback
    if fallback is None:
        return primary
    return min(primary, fallback)


def _host(url: str) -> str:
    parsed = urlparse(url)
    return parsed.hostname or ""
