from __future__ import annotations

from .browser import browser_act, browser_extract, browser_open
from typing import Any, Mapping

from .context import ToolContext, context_from_mapping, default_context
from .exec import shell_run
from .fs import fs_apply_patch, fs_list, fs_read, fs_search, fs_write
from .web import web_extract, web_fetch, web_search


class Toolset:
    def __init__(self, context: ToolContext | None = None, *, agent_context: Mapping[str, Any] | None = None) -> None:
        self._base_context = context or default_context()
        self._agent_context = agent_context

    @property
    def context(self) -> ToolContext:
        return self._base_context

    def _resolve_context(self, tool_name: str) -> ToolContext:
        if self._agent_context is None:
            return self._base_context
        return context_from_mapping(
            self._agent_context,
            base_context=self._base_context,
            tool_name=tool_name,
        )

    def web_search(
        self,
        query: str,
        max_results: int | None = None,
        recency: str | None = None,
        domains_allow: list[str] | None = None,
        domains_block: list[str] | None = None,
    ):
        return web_search(
            query,
            max_results=max_results,
            recency=recency,
            domains_allow=domains_allow,
            domains_block=domains_block,
            context=self._resolve_context("kantan_web_search"),
        )

    def web_fetch(
        self,
        url: str,
        headers: dict | None = None,
        method: str = "GET",
        timeout_ms: int | None = None,
    ):
        return web_fetch(
            url,
            headers=headers,
            method=method,
            timeout_ms=timeout_ms,
            context=self._resolve_context("kantan_web_fetch"),
        )

    def web_extract(
        self,
        html: str,
        mode: str = "markdown",
        max_chars: int | None = None,
    ):
        return web_extract(html, mode=mode, max_chars=max_chars, context=self._resolve_context("kantan_web_extract"))

    def browser_open(
        self,
        url: str,
        viewport: dict | None = None,
        timeout_ms: int | None = None,
    ):
        return browser_open(
            url,
            viewport=viewport,
            timeout_ms=timeout_ms,
            context=self._resolve_context("kantan_browser_open"),
        )

    def browser_act(
        self,
        page_id: str,
        actions: list[dict],
        timeout_ms: int | None = None,
    ):
        return browser_act(
            page_id,
            actions,
            timeout_ms=timeout_ms,
            context=self._resolve_context("kantan_browser_act"),
        )

    def browser_extract(
        self,
        page_id: str,
        selectors: list[str] | None = None,
        extract: list[str] | None = None,
    ):
        return browser_extract(
            page_id,
            selectors=selectors,
            extract=extract,
            context=self._resolve_context("kantan_browser_extract"),
        )

    def fs_list(
        self,
        path: str,
        glob: str | None = None,
        recursive: bool = False,
        max_entries: int | None = None,
    ):
        return fs_list(
            path,
            glob=glob,
            recursive=recursive,
            max_entries=max_entries,
            context=self._resolve_context("kantan_fs_list"),
        )

    def fs_search(
        self,
        root: str,
        pattern: str,
        file_glob: str | None = None,
        max_matches: int | None = None,
    ):
        return fs_search(
            root,
            pattern,
            file_glob=file_glob,
            max_matches=max_matches,
            context=self._resolve_context("kantan_fs_search"),
        )

    def fs_read(
        self,
        path: str,
        range: dict | None = None,
        head: int | None = None,
        tail: int | None = None,
        max_bytes: int | None = None,
    ):
        return fs_read(
            path,
            range=range,
            head=head,
            tail=tail,
            max_bytes=max_bytes,
            context=self._resolve_context("kantan_fs_read"),
        )

    def fs_write(
        self,
        path: str,
        text: str,
        mode: str,
    ):
        return fs_write(path, text, mode, context=self._resolve_context("kantan_fs_write"))

    def fs_apply_patch(
        self,
        patch: str,
        strip: int | None = None,
    ):
        return fs_apply_patch(patch, strip=strip, context=self._resolve_context("kantan_fs_apply_patch"))

    def shell_run(
        self,
        cmd: str | list[str],
        cwd: str | None = None,
        env: dict | None = None,
        timeout_ms: int | None = None,
    ):
        return shell_run(
            cmd,
            cwd=cwd,
            env=env,
            timeout_ms=timeout_ms,
            context=self._resolve_context("kantan_shell_run"),
        )


def default_toolset(cwd: str | None = None) -> Toolset:
    return Toolset(default_context(cwd))
