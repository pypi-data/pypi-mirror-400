from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ToolError:
    id: str
    type: str
    message: str


_ERROR_FORMATS: dict[str, str] = {
    "POLICY_DENIED": "[kt][E001] Policy denied: {detail}",
    "NOT_FOUND": "[kt][E002] Not found: {detail}",
    "INVALID_ARGUMENT": "[kt][E003] Invalid argument: {detail}",
    "TIMEOUT": "[kt][E004] Timeout: {detail}",
    "TOO_LARGE": "[kt][E005] Too large: {detail}",
    "NETWORK_ERROR": "[kt][E006] Network error: {detail}",
    "EXEC_ERROR": "[kt][E007] Exec error: {detail}",
    "INTERNAL_ERROR": "[kt][E008] Internal error: {detail}",
}

_ERROR_IDS: dict[str, str] = {
    "POLICY_DENIED": "KT-E001",
    "NOT_FOUND": "KT-E002",
    "INVALID_ARGUMENT": "KT-E003",
    "TIMEOUT": "KT-E004",
    "TOO_LARGE": "KT-E005",
    "NETWORK_ERROR": "KT-E006",
    "EXEC_ERROR": "KT-E007",
    "INTERNAL_ERROR": "KT-E008",
}


def build_error(error_type: str, detail: str) -> ToolError:
    fmt = _ERROR_FORMATS.get(error_type, "[kt][E008] Internal error: {detail}")
    message = fmt.format(detail=detail)
    return ToolError(id=_ERROR_IDS.get(error_type, "KT-E008"), type=error_type, message=message)


def error_response(error_type: str, detail: str, *, truncated: bool | None = None) -> dict:
    err = build_error(error_type, detail)
    payload: dict[str, object] = {"ok": False, "error": {"id": err.id, "type": err.type, "message": err.message}}
    if truncated is not None:
        payload["truncated"] = truncated
    return payload
