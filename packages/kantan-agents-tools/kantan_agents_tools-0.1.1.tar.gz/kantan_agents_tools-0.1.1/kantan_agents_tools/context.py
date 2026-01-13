from __future__ import annotations

import os
import uuid
from dataclasses import dataclass, fields
from typing import Any, Mapping

from .policy import Limits, PolicyConfig, PolicyEvaluator, default_policy_config
from .trace import NullTraceWriter, TraceWriter


@dataclass
class ToolContext:
    request_id: str
    policy: PolicyEvaluator
    tracer: TraceWriter
    limits: Limits


def default_context(cwd: str | None = None) -> ToolContext:
    base = cwd or os.getcwd()
    policy = PolicyEvaluator(default_policy_config(base))
    limits = Limits(
        max_read_bytes=256 * 1024,
        max_write_bytes=256 * 1024,
        max_output_chars=20000,
        max_fetch_bytes=512 * 1024,
        max_matches=200,
        max_actions=50,
        max_wait_ms=30000,
    )
    return ToolContext(request_id=uuid.uuid4().hex, policy=policy, tracer=NullTraceWriter(), limits=limits)


def context_from_mapping(
    context: Mapping[str, Any] | None,
    *,
    cwd: str | None = None,
    base_context: ToolContext | None = None,
    tool_name: str | None = None,
) -> ToolContext:
    # context["tool_rules"]["params"][tool_name] からToolContextを構築 / Build ToolContext from context["tool_rules"]["params"][tool_name].
    base = base_context or default_context(cwd)
    if not isinstance(context, Mapping):
        return base
    tool_config = _extract_tool_config(context, tool_name)
    if not isinstance(tool_config, Mapping):
        return base

    request_id = tool_config.get("request_id")
    if isinstance(request_id, str) and request_id:
        base = ToolContext(
            request_id=request_id,
            policy=base.policy,
            tracer=base.tracer,
            limits=base.limits,
        )

    tracer = tool_config.get("tracer")
    if tracer is not None and hasattr(tracer, "record"):
        base = ToolContext(
            request_id=base.request_id,
            policy=base.policy,
            tracer=tracer,
            limits=base.limits,
        )

    base_limits = _merge_limits(base.limits, tool_config.get("limits"))
    base_policy = _merge_policy(base.policy, tool_config.get("policy"), cwd or os.getcwd())
    return ToolContext(
        request_id=base.request_id,
        policy=base_policy,
        tracer=base.tracer,
        limits=base_limits,
    )


def _merge_limits(base: Limits, override: Any) -> Limits:
    if not isinstance(override, Mapping):
        return base
    data = {field.name: getattr(base, field.name) for field in fields(Limits)}
    for field in fields(Limits):
        if field.name in override:
            data[field.name] = override[field.name]
    return Limits(**data)


def _merge_policy(base: PolicyEvaluator, override: Any, cwd: str) -> PolicyEvaluator:
    if not isinstance(override, Mapping):
        return base
    base_config = base.config
    data = {field.name: getattr(base_config, field.name) for field in fields(PolicyConfig)}
    for field in fields(PolicyConfig):
        if field.name in override:
            data[field.name] = override[field.name]
    return PolicyEvaluator(PolicyConfig(**data))


def _extract_tool_config(context: Mapping[str, Any], tool_name: str | None) -> Mapping[str, Any] | None:
    tool_rules = context.get("tool_rules")
    if isinstance(tool_rules, Mapping):
        params = tool_rules.get("params")
        if isinstance(params, Mapping) and tool_name:
            tool_config = params.get(tool_name)
            if isinstance(tool_config, Mapping):
                return tool_config
    return None
