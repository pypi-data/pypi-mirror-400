from __future__ import annotations

import fnmatch
import os
import re
from typing import Iterable

from .context import ToolContext
from .errors import error_response
from .policy import PolicyAction
from .utils import truncate_text, with_trace

try:
    from unidiff import PatchSet
except Exception:  # pragma: no cover - optional dependency
    PatchSet = None

try:
    from pathspec import PathSpec
except Exception:  # pragma: no cover - optional dependency
    PathSpec = None


def fs_list(
    path: str,
    glob: str | None = None,
    recursive: bool = False,
    max_entries: int | None = None,
    *,
    context: ToolContext,
) -> dict:
    def run() -> dict:
        decision = context.policy.evaluate(PolicyAction(action_type="read_path", path=path))
        if not decision.allowed:
            return error_response("POLICY_DENIED", decision.reason)
        if not os.path.exists(path):
            return error_response("NOT_FOUND", path)
        entries: list[dict] = []
        limit = _resolve_limit(max_entries, context.limits.max_matches)
        excluded = set(context.policy.config.excluded_dir_names)
        gitignore = _load_gitignore(path) if context.policy.config.respect_gitignore else None
        if recursive:
            try:
                for root, dirs, files in os.walk(path):
                    dirs[:] = [
                        d
                        for d in dirs
                        if d not in excluded and not _is_gitignored(gitignore, os.path.join(root, d), True)
                    ]
                    for name in sorted(dirs + files):
                        full = os.path.join(root, name)
                        if glob and not fnmatch.fnmatch(name, glob):
                            continue
                        if _is_gitignored(gitignore, full, os.path.isdir(full)):
                            continue
                        entries.append(_entry_dict(full))
                        if limit is not None and len(entries) >= limit:
                            return {"entries": entries, "truncated": True}
            except OSError as exc:
                return error_response("INTERNAL_ERROR", str(exc))
        else:
            try:
                names = os.listdir(path)
            except OSError as exc:
                return error_response("INTERNAL_ERROR", str(exc))
            for name in sorted(names):
                if glob and not fnmatch.fnmatch(name, glob):
                    continue
                full = os.path.join(path, name)
                if _is_gitignored(gitignore, full, os.path.isdir(full)):
                    continue
                entries.append(_entry_dict(full))
                if limit is not None and len(entries) >= limit:
                    return {"entries": entries, "truncated": True}
        return {"entries": entries, "truncated": False}

    return with_trace(
        "fs_list",
        context.request_id,
        context.tracer,
        {"path": path, "glob": glob, "recursive": recursive, "max_entries": max_entries},
        run,
    )


def fs_search(
    root: str,
    pattern: str,
    file_glob: str | None = None,
    max_matches: int | None = None,
    *,
    context: ToolContext,
) -> dict:
    def run() -> dict:
        decision = context.policy.evaluate(PolicyAction(action_type="read_path", path=root))
        if not decision.allowed:
            return error_response("POLICY_DENIED", decision.reason)
        if not os.path.isdir(root):
            return error_response("NOT_FOUND", root)
        matches: list[dict] = []
        limit = _resolve_limit(max_matches, context.limits.max_matches)
        excluded = set(context.policy.config.excluded_dir_names)
        gitignore = _load_gitignore(root) if context.policy.config.respect_gitignore else None
        try:
            regex = re.compile(pattern)
        except re.error as exc:
            return error_response("INVALID_ARGUMENT", str(exc))
        try:
            for dirpath, dirnames, filenames in os.walk(root):
                dirnames[:] = [
                    d
                    for d in dirnames
                    if d not in excluded and not _is_gitignored(gitignore, os.path.join(dirpath, d), True)
                ]
                for filename in filenames:
                    if file_glob and not fnmatch.fnmatch(filename, file_glob):
                        continue
                    path = os.path.join(dirpath, filename)
                    if _is_gitignored(gitignore, path, False):
                        continue
                    if _is_binary(path):
                        continue
                    if context.limits.max_read_bytes is not None:
                        try:
                            size = os.path.getsize(path)
                        except OSError:
                            continue
                        if size > context.limits.max_read_bytes:
                            continue
                    try:
                        with open(path, "r", encoding="utf-8", errors="replace") as f:
                            for idx, line in enumerate(f, start=1):
                                match = regex.search(line)
                                if not match:
                                    continue
                                matches.append(
                                    {
                                        "path": path,
                                        "line": idx,
                                        "col": match.start() + 1,
                                        "preview": line.rstrip("\n"),
                                    }
                                )
                                if limit is not None and len(matches) >= limit:
                                    return {"matches": matches, "truncated": True}
                    except OSError:
                        continue
        except OSError as exc:
            return error_response("INTERNAL_ERROR", str(exc))
        return {"matches": matches, "truncated": False}

    return with_trace(
        "fs_search",
        context.request_id,
        context.tracer,
        {"root": root, "pattern": pattern, "file_glob": file_glob, "max_matches": max_matches},
        run,
    )


def fs_read(
    path: str,
    range: dict | None = None,
    head: int | None = None,
    tail: int | None = None,
    max_bytes: int | None = None,
    *,
    context: ToolContext,
) -> dict:
    def run() -> dict:
        decision = context.policy.evaluate(PolicyAction(action_type="read_path", path=path))
        if not decision.allowed:
            return error_response("POLICY_DENIED", decision.reason)
        if not os.path.exists(path):
            return error_response("NOT_FOUND", path)
        if _is_binary(path):
            return error_response("INVALID_ARGUMENT", "binary file")
        limit = _resolve_limit(max_bytes, context.limits.max_read_bytes)
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read() if limit is None else f.read(limit)
        except OSError as exc:
            return error_response("INTERNAL_ERROR", str(exc))
        truncated = False
        if limit is not None and os.path.getsize(path) > limit:
            truncated = True
        lines = content.splitlines()
        if range:
            start = max(1, int(range.get("start_line", 1)))
            end = int(range.get("end_line", start))
            lines = lines[start - 1 : end]
        elif head is not None:
            lines = lines[: max(0, head)]
        elif tail is not None:
            lines = lines[-max(0, tail) :]
        text = "\n".join(lines)
        text, text_truncated = truncate_text(text, context.limits.max_output_chars)
        truncated = truncated or text_truncated
        return {"text": text, "encoding": "utf-8", "truncated": truncated}

    return with_trace(
        "fs_read",
        context.request_id,
        context.tracer,
        {"path": path, "range": range, "head": head, "tail": tail, "max_bytes": max_bytes},
        run,
    )


def fs_write(
    path: str,
    text: str,
    mode: str,
    *,
    context: ToolContext,
) -> dict:
    def run() -> dict:
        decision = context.policy.evaluate(PolicyAction(action_type="write_path", path=path))
        if not decision.allowed:
            return error_response("POLICY_DENIED", decision.reason)
        if mode not in {"overwrite", "append", "create_only"}:
            return error_response("INVALID_ARGUMENT", f"unknown mode: {mode}")
        if mode == "create_only" and os.path.exists(path):
            return error_response("INVALID_ARGUMENT", "file already exists")
        data = text.encode("utf-8")
        if context.limits.max_write_bytes is not None and len(data) > context.limits.max_write_bytes:
            return error_response("TOO_LARGE", "write size exceeds limit")
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        except OSError as exc:
            return error_response("INTERNAL_ERROR", str(exc))
        file_mode = "a" if mode == "append" else "w"
        try:
            with open(path, file_mode, encoding="utf-8") as f:
                f.write(text)
        except OSError as exc:
            return error_response("INTERNAL_ERROR", str(exc))
        return {"ok": True, "bytes_written": len(data)}

    return with_trace(
        "fs_write",
        context.request_id,
        context.tracer,
        {"path": path, "mode": mode, "bytes": len(text.encode("utf-8"))},
        run,
    )


def fs_apply_patch(
    patch: str,
    strip: int | None = None,
    *,
    context: ToolContext,
) -> dict:
    def run() -> dict:
        if PatchSet is None:
            return error_response("INTERNAL_ERROR", "unidiff is not available")
        try:
            patch_set = PatchSet(patch)
        except Exception as exc:
            return error_response("INVALID_ARGUMENT", f"invalid patch: {exc}")
        applied: list[str] = []
        rejects: list[dict] = []
        for patched_file in patch_set:
            target_path = _strip_path(patched_file.path, strip)
            decision = context.policy.evaluate(PolicyAction(action_type="write_path", path=target_path))
            if not decision.allowed:
                rejects.append({"path": target_path, "reason": decision.reason})
                continue
            ok, reason = _apply_file_patch(target_path, patched_file)
            if ok:
                applied.append(target_path)
            else:
                rejects.append({"path": target_path, "reason": reason})
        return {"applied_files": applied, "rejects": rejects or None, "ok": not rejects}

    return with_trace(
        "fs_apply_patch",
        context.request_id,
        context.tracer,
        {"strip": strip, "patch_size": len(patch)},
        run,
    )


def _strip_path(path: str, strip: int | None) -> str:
    if not strip:
        return path
    parts = path.split("/")
    return "/".join(parts[strip:])


def _apply_file_patch(path: str, patched_file) -> tuple[bool, str]:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            source_lines = f.read().splitlines(keepends=True)
    except FileNotFoundError:
        source_lines = []
    except OSError as exc:
        return False, str(exc)

    output: list[str] = []
    src_index = 0
    for hunk in patched_file:
        hunk_start = max(0, hunk.source_start - 1)
        if hunk_start < src_index:
            return False, "hunk overlaps or is out of order"
        output.extend(source_lines[src_index:hunk_start])
        src_index = hunk_start
        for line in hunk:
            value = line.value
            if not value.endswith("\n"):
                value = value + "\n"
            if line.is_context:
                if src_index >= len(source_lines) or source_lines[src_index] != value:
                    return False, "context mismatch"
                output.append(source_lines[src_index])
                src_index += 1
            elif line.is_removed:
                if src_index >= len(source_lines) or source_lines[src_index] != value:
                    return False, "remove mismatch"
                src_index += 1
            elif line.is_added:
                output.append(value)
        # 次のハンクへ進む前に src_index は現状のまま / Keep src_index for next hunk.
    output.extend(source_lines[src_index:])

    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(output)
    except OSError as exc:
        return False, str(exc)
    return True, "applied"


def _entry_dict(path: str) -> dict:
    info = {
        "path": path,
        "type": "dir" if os.path.isdir(path) else "file",
    }
    try:
        stat = os.stat(path)
        info["size"] = stat.st_size
        info["mtime"] = int(stat.st_mtime)
    except OSError:
        return info
    return info


def _resolve_limit(primary: int | None, fallback: int | None) -> int | None:
    if primary is None:
        return fallback
    if fallback is None:
        return primary
    return min(primary, fallback)


def _is_binary(path: str) -> bool:
    try:
        with open(path, "rb") as f:
            chunk = f.read(1024)
    except OSError:
        return True
    return b"\x00" in chunk


def _load_gitignore(start_path: str) -> tuple[PathSpec, str] | None:
    # .gitignore を読み込み、パス判定のための spec を作る / Load .gitignore and build a matcher.
    if PathSpec is None:
        return None
    root = _find_gitignore_root(start_path)
    if not root:
        return None
    gitignore_path = os.path.join(root, ".gitignore")
    if not os.path.isfile(gitignore_path):
        return None
    try:
        with open(gitignore_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return None
    spec = PathSpec.from_lines("gitwildmatch", lines)
    return spec, root


def _find_gitignore_root(start_path: str) -> str | None:
    # .git があれば repo ルート、無ければ最初に見つかった .gitignore を使う / Prefer repo root if .git exists.
    current = os.path.abspath(start_path)
    if os.path.isfile(current):
        current = os.path.dirname(current)
    found_gitignore = None
    while True:
        if os.path.isdir(os.path.join(current, ".git")):
            return current
        if found_gitignore is None and os.path.isfile(os.path.join(current, ".gitignore")):
            found_gitignore = current
        parent = os.path.dirname(current)
        if parent == current:
            return found_gitignore
        current = parent


def _is_gitignored(spec_info: tuple[PathSpec, str] | None, path: str, is_dir: bool) -> bool:
    # root 配下の相対パスで判定する / Match using paths relative to the gitignore root.
    if spec_info is None:
        return False
    spec, root = spec_info
    try:
        rel = os.path.relpath(path, root)
    except ValueError:
        return False
    if rel in {".", ""} or rel.startswith(".."):
        return False
    rel = rel.replace(os.sep, "/")
    if is_dir and not rel.endswith("/"):
        rel = rel + "/"
    return spec.match_file(rel)
