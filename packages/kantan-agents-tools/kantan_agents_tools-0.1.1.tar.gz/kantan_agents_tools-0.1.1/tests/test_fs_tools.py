from __future__ import annotations

from pathlib import Path

from kantan_agents_tools.context import ToolContext
from kantan_agents_tools.fs import fs_apply_patch, fs_list, fs_read, fs_search, fs_write
from kantan_agents_tools.policy import Limits, PolicyConfig, PolicyEvaluator
from kantan_agents_tools.trace import NullTraceWriter


def _make_context(base_path: Path, *, respect_gitignore: bool = True) -> ToolContext:
    policy = PolicyEvaluator(
        PolicyConfig(
            allowed_read_paths=[str(base_path)],
            allowed_write_paths=[str(base_path)],
            respect_gitignore=respect_gitignore,
        )
    )
    limits = Limits(
        max_read_bytes=4096,
        max_write_bytes=4096,
        max_output_chars=20000,
        max_fetch_bytes=4096,
        max_matches=100,
    )
    return ToolContext(request_id="test", policy=policy, tracer=NullTraceWriter(), limits=limits)


def test_fs_list_read_write_apply_patch(tmp_path: Path) -> None:
    context = _make_context(tmp_path)
    target = tmp_path / "sample.txt"

    write_result = fs_write(str(target), "old\n", "overwrite", context=context)
    assert write_result["ok"] is True

    list_result = fs_list(str(tmp_path), context=context)
    listed_paths = {entry["path"] for entry in list_result["entries"]}
    assert str(target) in listed_paths

    read_result = fs_read(str(target), context=context)
    assert read_result["text"].strip() == "old"

    patch = (
        f"--- {target}\n"
        f"+++ {target}\n"
        "@@ -1,1 +1,1 @@\n"
        "-old\n"
        "+new\n"
    )
    patch_result = fs_apply_patch(patch, context=context)
    assert patch_result["ok"] is True

    updated = fs_read(str(target), context=context)
    assert updated["text"].strip() == "new"


def test_fs_search_finds_matches(tmp_path: Path) -> None:
    context = _make_context(tmp_path)
    target = tmp_path / "search.txt"
    fs_write(str(target), "alpha\nbeta\ngamma\n", "overwrite", context=context)

    search_result = fs_search(str(tmp_path), "beta", context=context)
    assert search_result["truncated"] is False
    assert any(match["path"] == str(target) for match in search_result["matches"])


def test_fs_list_search_respect_gitignore(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text("ignored.txt\nignored_dir/\n", encoding="utf-8")
    (tmp_path / "ignored.txt").write_text("ignored", encoding="utf-8")
    (tmp_path / "keep.txt").write_text("keep", encoding="utf-8")
    ignored_dir = tmp_path / "ignored_dir"
    ignored_dir.mkdir()
    (ignored_dir / "inside.txt").write_text("ignored", encoding="utf-8")

    context = _make_context(tmp_path)
    listed = fs_list(str(tmp_path), recursive=True, context=context)
    paths = {entry["path"] for entry in listed["entries"]}
    assert str(tmp_path / "keep.txt") in paths
    assert str(tmp_path / "ignored.txt") not in paths
    assert str(ignored_dir) not in paths

    search = fs_search(str(tmp_path), "ignored", context=context)
    assert all("ignored" not in match["path"] for match in search["matches"])

    context_no_ignore = _make_context(tmp_path, respect_gitignore=False)
    listed_no_ignore = fs_list(str(tmp_path), recursive=True, context=context_no_ignore)
    paths_no_ignore = {entry["path"] for entry in listed_no_ignore["entries"]}
    assert str(tmp_path / "ignored.txt") in paths_no_ignore
