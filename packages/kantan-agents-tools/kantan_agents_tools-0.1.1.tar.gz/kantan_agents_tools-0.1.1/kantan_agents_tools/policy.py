from __future__ import annotations

import os
import shlex
from dataclasses import dataclass, field
from typing import Iterable
from urllib.parse import urlparse


@dataclass
class Limits:
    max_read_bytes: int | None = None
    max_write_bytes: int | None = None
    max_output_chars: int | None = None
    max_fetch_bytes: int | None = None
    max_matches: int | None = None
    max_actions: int | None = None
    max_wait_ms: int | None = None


@dataclass
class PolicyConfig:
    allowed_read_paths: list[str] | None = None
    allowed_write_paths: list[str] | None = None
    allowed_domains: list[str] | None = None
    blocked_domains: list[str] | None = None
    allowed_commands: list[str] | None = None
    blocked_commands: list[str] | None = None
    # 検索プロバイダの優先設定 / Search provider preference.
    search_provider: str = "auto"
    # .gitignore を尊重するか / Respect .gitignore files.
    respect_gitignore: bool = True
    excluded_dir_names: list[str] = field(
        default_factory=lambda: [".git", "node_modules", ".venv", "__pycache__"]
    )


@dataclass(frozen=True)
class PolicyAction:
    action_type: str
    path: str | None = None
    url: str | None = None
    command: str | list[str] | None = None
    cwd: str | None = None


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str


class PolicyEvaluator:
    def __init__(self, config: PolicyConfig) -> None:
        self._config = config

    @property
    def config(self) -> PolicyConfig:
        return self._config

    def evaluate(self, action: PolicyAction) -> PolicyDecision:
        if action.action_type in {"read_path", "write_path"}:
            return self._evaluate_path(action)
        if action.action_type in {"fetch_url", "open_url"}:
            return self._evaluate_url(action)
        if action.action_type == "shell_run":
            return self._evaluate_command(action)
        return PolicyDecision(True, "allowed")

    def _evaluate_path(self, action: PolicyAction) -> PolicyDecision:
        target = action.path
        if not target:
            return PolicyDecision(False, "path is required")
        allowed = (
            self._config.allowed_read_paths
            if action.action_type == "read_path"
            else self._config.allowed_write_paths
        )
        if not allowed:
            return PolicyDecision(True, "allowed")
        if _is_path_allowed(target, allowed):
            return PolicyDecision(True, "allowed")
        return PolicyDecision(False, f"path not allowed: {target}")

    def _evaluate_url(self, action: PolicyAction) -> PolicyDecision:
        if not action.url:
            return PolicyDecision(False, "url is required")
        parsed = urlparse(action.url)
        domain = parsed.hostname or ""
        if self._config.blocked_domains and domain in self._config.blocked_domains:
            return PolicyDecision(False, f"blocked domain: {domain}")
        if self._config.allowed_domains and domain not in self._config.allowed_domains:
            return PolicyDecision(False, f"domain not allowed: {domain}")
        return PolicyDecision(True, "allowed")

    def _evaluate_command(self, action: PolicyAction) -> PolicyDecision:
        if action.command is None:
            return PolicyDecision(False, "command is required")
        if isinstance(action.command, str):
            tokens = shlex.split(action.command)
        else:
            tokens = list(action.command)
        cmd = tokens[0] if tokens else ""
        if self._config.blocked_commands and cmd in self._config.blocked_commands:
            return PolicyDecision(False, f"blocked command: {cmd}")
        if self._config.allowed_commands and cmd not in self._config.allowed_commands:
            return PolicyDecision(False, f"command not allowed: {cmd}")
        if action.cwd and self._config.allowed_write_paths:
            if not _is_path_allowed(action.cwd, self._config.allowed_write_paths):
                return PolicyDecision(False, f"cwd not allowed: {action.cwd}")
        return PolicyDecision(True, "allowed")


def default_policy_config(cwd: str) -> PolicyConfig:
    return PolicyConfig(
        allowed_read_paths=[cwd],
        allowed_write_paths=[cwd],
    )


def _is_path_allowed(path: str, allowed_paths: Iterable[str]) -> bool:
    # ルート配下かを解決後パスで判定する / Check containment using resolved paths.
    real_target = os.path.realpath(path)
    for allowed in allowed_paths:
        real_allowed = os.path.realpath(allowed)
        try:
            if os.path.commonpath([real_allowed, real_target]) == real_allowed:
                return True
        except ValueError:
            continue
    return False
