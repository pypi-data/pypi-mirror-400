# kantan-agents-tools

A ready-to-use basic tool pack for kantan-agents (Web/Browser/FS/Exec).  
All tool usage is controlled through `tool_rules` for consistent safety and reproducibility.

## What problems it solves
- You need a ready-to-use set of basic tools for kantan-agents to start fast.
- Tool interfaces and configs vary across providers, increasing learning cost.
- Agents can accidentally touch unexpected paths, domains, or commands.
- It is hard to trace what ran and which limits were applied.

kantan-agents-tools bundles basic tools and centralizes allow/deny, input validation, and policy/limits under `tool_rules`
so you can safely repeat "research -> fetch -> operate -> edit -> execute".

## Tool list
### Web
- `kantan_web_search`: return candidate URLs from search
- `kantan_web_fetch`: fetch HTML/text from a URL
- `kantan_web_extract`: extract main text from HTML

### Browser
- `kantan_browser_open`: open dynamic pages and return a `page_id`
- `kantan_browser_act`: run actions like click/input/wait
- `kantan_browser_extract`: extract text/links/tables from DOM

### FileSystem
- `kantan_fs_list`: list directory entries
- `kantan_fs_search`: search file contents
- `kantan_fs_read`: read a file safely
- `kantan_fs_write`: create/overwrite/append a file
- `kantan_fs_apply_patch`: apply a unified diff

### Exec
- `kantan_shell_run`: run a command

## About the kantan stack
The kantan stack separates the LLM, agent runtime, tools, and your app into thin layers:

- `kantan-llm`: minimal interface for LLM calls
- `kantan-agents`: agent runtime and `tool_rules` governance
- `kantan-agents-tools`: this basic tool pack
- your app: workflow and domain logic

This separation keeps safety and reproducibility while allowing clean replacement and extension.

## Install

```bash
# 基本ツールを追加 / Add core tools.
uv add kantan-agents kantan-agents-tools

# ブラウザ系ツールを使う場合 / When using browser tools.
uv add playwright
python -m playwright install chromium
```

## Quick Start (Agent)
kantan-agents discovers tool providers via entry points.  
Use `tool_rules` to allow tools and to configure validation + tool settings.

```python
from kantan_agents import Agent, ToolRulesMode, get_context_with_tool_rules

agent = Agent(
    name="tools-agent",
    instructions="Use kantan_web_search to find references.",
    model="gpt-5-mini",  # モデルを明示 / Explicit model.
)

context = get_context_with_tool_rules(ToolRulesMode.RECOMMENDED)  # 推奨ルールを作成 / Build recommended rules.
context["tool_rules"]["allow"] = ["kantan_web_search"]  # 検索のみ許可 / Allow search only.
context["tool_rules"]["params"] = {
    "kantan_web_search": {
        "max_results": {"type": "integer", "minimum": 1, "maximum": 5},  # 入力バリデーション / Input validation.
        "policy": {"allowed_domains": ["example.com"], "search_provider": "auto"},  # 許可ドメイン / Allowed domains.
        "limits": {"max_fetch_bytes": 512000, "max_output_chars": 20000, "max_matches": 200},  # 出力上限 / Output limits.
        "request_id": "req-001",  # 追跡ID / Request ID.
    }
}

result = agent.run("Search for kantan-agents.", context=context)
print(result["result"].final_output)  # 結果を表示 / Print the result.
```

Notes:
- `tool_rules.params` is used for both input validation and tool settings.
- Reserved keys for tool settings: `policy` / `limits` / `tracer` / `request_id`.

## Direct Call (Non-agent)

```python
from kantan_agents_tools import default_toolset

toolset = default_toolset()
print(toolset.fs_list("."))
```

## Testing

```bash
uv run pytest
```

## Docs
- `docs/tool_usage.md`
- `docs/spec.md`
- `docs/architecture.md`
