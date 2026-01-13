from __future__ import annotations

"""Canonicalization helpers for graph keys."""

import re
from urllib.parse import unquote, urlsplit, urlunsplit


def _collapse_ws(value: str) -> str:
    return " ".join(value.split())


def _normalize_key_part(value: str) -> str:
    return _collapse_ws(value).strip().lower()


def normalize_connection_key(key: str) -> str:
    """Normalize connection keys for stable cross-backend dedupe."""
    parts = key.split("|")
    return "|".join(_normalize_key_part(part) for part in parts)


def _normalize_file_value(value: str) -> str:
    v = value.strip()
    if v.lower().startswith("file://"):
        parsed = urlsplit(v)
        v = unquote(parsed.path or "")
    v = v.replace("\\", "/")
    v = re.sub(r"/{2,}", "/", v)
    if re.match(r"^/[A-Za-z]:/", v):
        v = v[1:]
    return v.lower()


def _normalize_url_value(value: str) -> str:
    v = value.strip()
    try:
        parsed = urlsplit(v)
    except Exception:  # noqa: BLE001
        return v.lower()
    if not parsed.scheme and not parsed.netloc:
        return v.lower()
    return urlunsplit(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path or "",
            parsed.query or "",
            parsed.fragment or "",
        )
    )


def _normalize_source_value(source_type: str, value: str) -> str:
    base = _collapse_ws(value).strip()
    if not base:
        return ""
    if source_type == "file":
        return _normalize_file_value(base)
    if source_type in {"web", "sharepoint"}:
        return _normalize_url_value(base)
    return base.lower()


def normalize_source_key(key: str) -> str:
    """Normalize source keys for stable cross-backend dedupe."""
    parts = key.split("|")
    if not parts:
        return _normalize_key_part(key)
    source_type = _normalize_key_part(parts[0])
    normalized = [source_type]
    normalized.extend(_normalize_source_value(source_type, part) for part in parts[1:])
    return "|".join(normalized)
