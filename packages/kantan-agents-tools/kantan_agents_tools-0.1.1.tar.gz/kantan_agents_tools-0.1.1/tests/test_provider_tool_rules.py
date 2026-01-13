from __future__ import annotations

from kantan_agents_tools.provider import KantanToolProvider


def test_provider_get_tool_rules_includes_all_tools() -> None:
    provider = KantanToolProvider()
    rules = provider.get_tool_rules()

    assert rules is not None
    assert rules["allow"] is None
    assert rules["deny"] is None

    expected_tools = {
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
    }
    assert set(rules["params"].keys()) == expected_tools


def test_provider_get_tool_rules_returns_independent_copy() -> None:
    provider = KantanToolProvider()
    rules = provider.get_tool_rules()

    rules["params"]["kantan_web_search"]["query"]["maxLength"] = 1
    fresh = provider.get_tool_rules()

    assert fresh["params"]["kantan_web_search"]["query"]["maxLength"] == 200
