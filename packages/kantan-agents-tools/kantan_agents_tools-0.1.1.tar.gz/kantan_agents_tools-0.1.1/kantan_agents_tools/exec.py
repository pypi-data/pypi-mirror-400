from __future__ import annotations

import shlex
import subprocess

from .context import ToolContext
from .errors import error_response
from .policy import PolicyAction
from .utils import truncate_text, with_trace


def shell_run(
    cmd: str | list[str],
    cwd: str | None = None,
    env: dict | None = None,
    timeout_ms: int | None = None,
    *,
    context: ToolContext,
) -> dict:
    def run() -> dict:
        decision = context.policy.evaluate(
            PolicyAction(action_type="shell_run", command=cmd, cwd=cwd or "")
        )
        if not decision.allowed:
            return error_response("POLICY_DENIED", decision.reason)
        if isinstance(cmd, str):
            args = shlex.split(cmd)
        else:
            args = list(cmd)
        if not args:
            return error_response("INVALID_ARGUMENT", "empty command")
        try:
            result = subprocess.run(
                args,
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                timeout=(timeout_ms or 10000) / 1000,
            )
        except subprocess.TimeoutExpired:
            return error_response("TIMEOUT", "command timed out")
        except Exception as exc:
            return error_response("EXEC_ERROR", str(exc))
        stdout, stdout_truncated = truncate_text(result.stdout, context.limits.max_output_chars)
        stderr, stderr_truncated = truncate_text(result.stderr, context.limits.max_output_chars)
        return {
            "exit_code": result.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "truncated": stdout_truncated or stderr_truncated,
        }

    return with_trace(
        "shell_run",
        context.request_id,
        context.tracer,
        {"cmd": cmd, "cwd": cwd, "timeout_ms": timeout_ms},
        run,
    )
