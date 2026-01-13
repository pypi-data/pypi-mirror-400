from __future__ import annotations

import sys
from pathlib import Path

from kantan_agents_tools.context import ToolContext
from kantan_agents_tools.exec import shell_run
from kantan_agents_tools.policy import Limits, PolicyConfig, PolicyEvaluator
from kantan_agents_tools.trace import NullTraceWriter


def _make_context(base_path: Path, allowed_commands: list[str] | None) -> ToolContext:
    policy = PolicyEvaluator(
        PolicyConfig(
            allowed_read_paths=[str(base_path)],
            allowed_write_paths=[str(base_path)],
            allowed_commands=allowed_commands,
        )
    )
    limits = Limits(max_output_chars=20000)
    return ToolContext(request_id="test", policy=policy, tracer=NullTraceWriter(), limits=limits)


def test_shell_run_allows_command(tmp_path: Path) -> None:
    cmd = [sys.executable, "-c", "print('hi')"]
    context = _make_context(tmp_path, [sys.executable])

    result = shell_run(cmd, context=context)

    assert result["exit_code"] == 0
    assert "hi" in result["stdout"]


def test_shell_run_denies_command(tmp_path: Path) -> None:
    cmd = [sys.executable, "-c", "print('hi')"]
    context = _make_context(tmp_path, ["echo"])

    result = shell_run(cmd, context=context)

    assert result["ok"] is False
    assert result["error"]["type"] == "POLICY_DENIED"
