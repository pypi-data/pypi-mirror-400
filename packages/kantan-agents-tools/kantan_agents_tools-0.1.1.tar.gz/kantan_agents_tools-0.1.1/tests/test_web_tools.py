from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from kantan_agents_tools.context import ToolContext
from kantan_agents_tools.policy import Limits, PolicyConfig, PolicyEvaluator
from kantan_agents_tools.trace import NullTraceWriter
from kantan_agents_tools.web import web_extract, web_fetch, web_search


def _make_context(base_path: Path, *, search_provider: str = "auto") -> ToolContext:
    policy = PolicyEvaluator(
        PolicyConfig(
            allowed_read_paths=[str(base_path)],
            allowed_write_paths=[str(base_path)],
            allowed_domains=["127.0.0.1"],
            search_provider=search_provider,
        )
    )
    limits = Limits(
        max_output_chars=20000,
        max_fetch_bytes=4096,
        max_matches=5,
    )
    return ToolContext(request_id="test", policy=policy, tracer=NullTraceWriter(), limits=limits)


class _Handler(BaseHTTPRequestHandler):
    body = b""
    content_type = "text/html; charset=utf-8"

    def do_GET(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", self.content_type)
        self.send_header("Content-Length", str(len(self.body)))
        self.end_headers()
        self.wfile.write(self.body)

    def log_message(self, format: str, *args) -> None:
        return


def _start_server(body: bytes) -> tuple[ThreadingHTTPServer, threading.Thread]:
    _Handler.body = body
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return server, thread


def test_web_fetch_extract_local(tmp_path: Path) -> None:
    body = b"<html><body><h1>Hello</h1></body></html>"
    server, thread = _start_server(body)
    try:
        context = _make_context(tmp_path)
        url = f"http://127.0.0.1:{server.server_port}/"
        fetched = web_fetch(url, context=context)
        assert fetched["status"] == 200
        extracted = web_extract(fetched["body"], context=context)
        assert "Hello" in extracted["text"]
    finally:
        server.shutdown()
        thread.join()


def test_web_search_invalid_provider(tmp_path: Path) -> None:
    context = _make_context(tmp_path, search_provider="invalid")

    result = web_search("query", context=context)

    assert result["ok"] is False
    assert result["error"]["type"] == "INVALID_ARGUMENT"


def test_web_search_tavily_requires_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    context = _make_context(tmp_path, search_provider="tavily")

    result = web_search("query", context=context)

    assert result["ok"] is False
    assert result["error"]["type"] == "INVALID_ARGUMENT"
