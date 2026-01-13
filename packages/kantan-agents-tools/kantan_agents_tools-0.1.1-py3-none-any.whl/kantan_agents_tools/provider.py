from __future__ import annotations

import asyncio
import copy
import json
from typing import Any, Callable

import agents
from agents.tool import FunctionTool

from .context import ToolContext, context_from_mapping, default_context
from .errors import error_response
from .fs import fs_apply_patch, fs_list, fs_read, fs_search, fs_write
from .web import web_extract, web_fetch, web_search
from .browser import browser_act, browser_extract, browser_open
from .exec import shell_run


class KantanToolProvider:
    def __init__(self, context: ToolContext | None = None) -> None:
        self._context = context or default_context()
        self._tools = _build_tools(self._context)

    def list_tools(self) -> list[Any]:
        return list(self._tools)

    def get_tool_rules(self) -> dict[str, Any] | None:
        return _build_tool_rules()


_TOOL_NAMES = [
    "kantan_web_search",
    "kantan_web_fetch",
    "kantan_web_extract",
    "kantan_browser_open",
    "kantan_browser_act",
    "kantan_browser_extract",
    "kantan_fs_list",
    "kantan_fs_search",
    "kantan_fs_read",
    "kantan_fs_write",
    "kantan_fs_apply_patch",
    "kantan_shell_run",
]

_TOOL_RULES_PARAMS: dict[str, dict[str, Any]] = {
    "kantan_web_search": {
        "query": {"type": "string", "minLength": 1, "maxLength": 200},
        "max_results": {"type": "integer", "minimum": 1, "maximum": 50},
        "recency": {"type": "string"},
        "domains_allow": {"type": "array"},
        "domains_block": {"type": "array"},
    },
    "kantan_web_fetch": {
        "url": {"type": "string", "minLength": 1, "maxLength": 2048},
        "headers": {"type": "object"},
        "method": {"type": "string", "enum": ["GET", "POST"]},
        "timeout_ms": {"type": "integer", "minimum": 1},
    },
    "kantan_web_extract": {
        "html": {"type": "string", "minLength": 1},
        "mode": {"type": "string", "enum": ["text", "markdown"]},
        "max_chars": {"type": "integer", "minimum": 1},
    },
    "kantan_browser_open": {
        "url": {"type": "string", "minLength": 1, "maxLength": 2048},
        "viewport": {"type": "object"},
        "timeout_ms": {"type": "integer", "minimum": 1},
    },
    "kantan_browser_act": {
        "page_id": {"type": "string", "minLength": 1},
        "actions": {"type": "array"},
        "timeout_ms": {"type": "integer", "minimum": 1},
    },
    "kantan_browser_extract": {
        "page_id": {"type": "string", "minLength": 1},
        "selectors": {"type": "array"},
        "extract": {"type": "array"},
    },
    "kantan_fs_list": {
        "path": {"type": "string", "minLength": 1},
        "glob": {"type": "string"},
        "recursive": {"type": "boolean"},
        "max_entries": {"type": "integer", "minimum": 1},
    },
    "kantan_fs_search": {
        "root": {"type": "string", "minLength": 1},
        "pattern": {"type": "string", "minLength": 1},
        "file_glob": {"type": "string"},
        "max_matches": {"type": "integer", "minimum": 1},
    },
    "kantan_fs_read": {
        "path": {"type": "string", "minLength": 1},
        "range": {"type": "object"},
        "head": {"type": "integer", "minimum": 1},
        "tail": {"type": "integer", "minimum": 1},
        "max_bytes": {"type": "integer", "minimum": 1},
    },
    "kantan_fs_write": {
        "path": {"type": "string", "minLength": 1},
        "text": {"type": "string"},
        "mode": {"type": "string", "enum": ["overwrite", "append", "create_only"]},
    },
    "kantan_fs_apply_patch": {
        "patch": {"type": "string", "minLength": 1},
        "strip": {"type": "integer", "minimum": 0},
    },
    "kantan_shell_run": {
        "cwd": {"type": "string"},
        "env": {"type": "object"},
        "timeout_ms": {"type": "integer", "minimum": 1},
    },
}


def _build_tool_rules() -> dict[str, Any]:
    return {
        "allow": None,
        "deny": None,
        "params": copy.deepcopy(_TOOL_RULES_PARAMS),
    }


def _build_tools(context: ToolContext) -> list[FunctionTool]:
    return [
        _make_tool("kantan_web_search", _schema_web_search, web_search, context),
        _make_tool("kantan_web_fetch", _schema_web_fetch, web_fetch, context),
        _make_tool("kantan_web_extract", _schema_web_extract, web_extract, context),
        _make_tool("kantan_browser_open", _schema_browser_open, browser_open, context),
        _make_tool("kantan_browser_act", _schema_browser_act, browser_act, context),
        _make_tool("kantan_browser_extract", _schema_browser_extract, browser_extract, context),
        _make_tool("kantan_fs_list", _schema_fs_list, fs_list, context),
        _make_tool("kantan_fs_search", _schema_fs_search, fs_search, context),
        _make_tool("kantan_fs_read", _schema_fs_read, fs_read, context),
        _make_tool("kantan_fs_write", _schema_fs_write, fs_write, context),
        _make_tool("kantan_fs_apply_patch", _schema_fs_apply_patch, fs_apply_patch, context),
        _make_tool("kantan_shell_run", _schema_shell_run, shell_run, context),
    ]


def _make_tool(
    name: str,
    schema_fn: Callable[..., Any],
    handler: Callable[..., dict],
    base_context: ToolContext,
) -> FunctionTool:
    schema_tool = agents.function_tool(schema_fn, name_override=name, strict_mode=False)

    async def _on_invoke_tool(ctx, input_text: str) -> Any:
        payload, error = _parse_input(input_text)
        if error is not None:
            return error
        tool_context = context_from_mapping(
            getattr(ctx, "context", None),
            base_context=base_context,
            tool_name=name,
        )
        return await asyncio.to_thread(_invoke_handler, handler, payload, tool_context)

    return FunctionTool(
        name=schema_tool.name,
        description=schema_tool.description,
        params_json_schema=schema_tool.params_json_schema,
        on_invoke_tool=_on_invoke_tool,
        strict_json_schema=schema_tool.strict_json_schema,
        tool_input_guardrails=schema_tool.tool_input_guardrails,
        tool_output_guardrails=schema_tool.tool_output_guardrails,
        is_enabled=schema_tool.is_enabled,
    )


def _parse_input(input_text: str) -> tuple[dict[str, Any], dict | None]:
    if not input_text:
        return {}, None
    try:
        payload = json.loads(input_text)
    except Exception as exc:
        return {}, error_response("INVALID_ARGUMENT", f"tool input must be JSON object: {exc}")
    if not isinstance(payload, dict):
        return {}, error_response("INVALID_ARGUMENT", "tool input must be JSON object")
    return payload, None


def _invoke_handler(handler: Callable[..., dict], payload: dict[str, Any], tool_context) -> dict:
    try:
        return handler(**payload, context=tool_context)
    except TypeError as exc:
        return error_response("INVALID_ARGUMENT", str(exc))
    except Exception as exc:  # pragma: no cover - safety net
        return error_response("INTERNAL_ERROR", str(exc))


# Schema functions for strict JSON schema generation. / 厳格なJSONスキーマ生成用の関数。


def _schema_web_search(
    query: str,
    max_results: int | None = None,
    recency: str | None = None,
    domains_allow: list[str] | None = None,
    domains_block: list[str] | None = None,
) -> None:
    """Web検索を行う / Search the web for relevant URLs."""
    return None


def _schema_web_fetch(
    url: str,
    headers: dict | None = None,
    method: str = "GET",
    timeout_ms: int | None = None,
) -> None:
    """URLから本文を取得する / Fetch a URL and return content."""
    return None


def _schema_web_extract(
    html: str,
    mode: str = "markdown",
    max_chars: int | None = None,
) -> None:
    """HTMLから本文を抽出する / Extract text from HTML content."""
    return None


def _schema_browser_open(
    url: str,
    viewport: dict | None = None,
    timeout_ms: int | None = None,
) -> None:
    """動的ページを開く / Open a dynamic page in a browser."""
    return None


def _schema_browser_act(
    page_id: str,
    actions: list[dict],
    timeout_ms: int | None = None,
) -> None:
    """ページ上で操作を行う / Perform browser actions on a page."""
    return None


def _schema_browser_extract(
    page_id: str,
    selectors: list[str] | None = None,
    extract: list[str] | None = None,
) -> None:
    """ページから情報を抽出する / Extract text/links/tables from a page."""
    return None


def _schema_fs_list(
    path: str,
    glob: str | None = None,
    recursive: bool = False,
    max_entries: int | None = None,
) -> None:
    """ディレクトリを列挙する / List directory entries."""
    return None


def _schema_fs_search(
    root: str,
    pattern: str,
    file_glob: str | None = None,
    max_matches: int | None = None,
) -> None:
    """ファイル内検索を行う / Search files for a pattern."""
    return None


def _schema_fs_read(
    path: str,
    range: dict | None = None,
    head: int | None = None,
    tail: int | None = None,
    max_bytes: int | None = None,
) -> None:
    """ファイルを安全に読む / Read file contents safely."""
    return None


def _schema_fs_write(
    path: str,
    text: str,
    mode: str,
) -> None:
    """ファイルに書き込む / Write or append to a file."""
    return None


def _schema_fs_apply_patch(
    patch: str,
    strip: int | None = None,
) -> None:
    """パッチを適用する / Apply a unified diff patch."""
    return None


def _schema_shell_run(
    cmd: str | list[str],
    cwd: str | None = None,
    env: dict | None = None,
    timeout_ms: int | None = None,
) -> None:
    """コマンドを実行する / Run a shell command."""
    return None
