from __future__ import annotations

from kantan_agents_tools.context import ToolContext, context_from_mapping
from kantan_agents_tools.policy import Limits, PolicyConfig, PolicyEvaluator
from kantan_agents_tools.trace import InMemoryTraceWriter, NullTraceWriter


def _make_base_context() -> ToolContext:
    policy = PolicyEvaluator(
        PolicyConfig(
            allowed_read_paths=["/base/read"],
            allowed_write_paths=["/base/write"],
            allowed_domains=["example.com"],
            blocked_domains=["blocked.example.com"],
            allowed_commands=["echo"],
            blocked_commands=["rm"],
            search_provider="auto",
            excluded_dir_names=[".git", "node_modules"],
        )
    )
    limits = Limits(
        max_read_bytes=100,
        max_write_bytes=200,
        max_output_chars=300,
        max_fetch_bytes=400,
        max_matches=500,
        max_actions=6,
        max_wait_ms=700,
    )
    return ToolContext(request_id="base-id", policy=policy, tracer=NullTraceWriter(), limits=limits)


def test_context_from_mapping_uses_tool_rules_params() -> None:
    base = _make_base_context()
    tracer = InMemoryTraceWriter()
    context = {
        "tool_rules": {
            "allow": ["kantan_fs_read"],
            "deny": [],
            "params": {
                "kantan_fs_read": {
                    "request_id": "req-123",
                    "tracer": tracer,
                    "limits": {
                        "max_read_bytes": 1024,
                        "max_output_chars": 2048,
                    },
                    "policy": {
                        "allowed_read_paths": ["/override/read"],
                        "search_provider": "tavily",
                    },
                }
            },
        }
    }

    resolved = context_from_mapping(context, base_context=base, tool_name="kantan_fs_read")

    assert resolved.request_id == "req-123"
    assert resolved.tracer is tracer
    assert resolved.limits.max_read_bytes == 1024
    assert resolved.limits.max_output_chars == 2048
    assert resolved.limits.max_write_bytes == 200
    assert resolved.policy.config.allowed_read_paths == ["/override/read"]
    assert resolved.policy.config.allowed_write_paths == ["/base/write"]
    assert resolved.policy.config.search_provider == "tavily"


def test_context_from_mapping_ignores_legacy_tools_params() -> None:
    base = _make_base_context()
    context = {
        "tools": {
            "params": {
                "kantan_fs_read": {
                    "request_id": "legacy-id",
                }
            }
        }
    }

    resolved = context_from_mapping(context, base_context=base, tool_name="kantan_fs_read")

    assert resolved.request_id == "base-id"


def test_context_from_mapping_requires_matching_tool_name() -> None:
    base = _make_base_context()
    context = {
        "tool_rules": {
            "params": {
                "kantan_fs_read": {
                    "request_id": "req-999",
                }
            }
        }
    }

    resolved = context_from_mapping(context, base_context=base, tool_name="kantan_fs_write")

    assert resolved.request_id == "base-id"
