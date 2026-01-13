from __future__ import annotations

from excelminer.backends.com_backend import _safe_jsonish


class DummyComProxy:
    def __init__(self) -> None:
        # Mimic pywin32 COM proxy marker.
        self._oleobj_ = object()


def test_safe_jsonish_replaces_com_proxies() -> None:
    payload = {
        "ok": "value",
        "proxy": DummyComProxy(),
        "nested": {"p2": DummyComProxy(), "n": 1},
        "list": [DummyComProxy(), 2, "x"],
    }

    safe = _safe_jsonish(payload)

    assert safe["ok"] == "value"
    assert isinstance(safe["proxy"], str) and safe["proxy"].startswith("<com:")
    assert isinstance(safe["nested"]["p2"], str) and safe["nested"]["p2"].startswith(
        "<com:"
    )
    assert isinstance(safe["list"][0], str) and safe["list"][0].startswith("<com:")


def test_safe_jsonish_truncates_huge_strings() -> None:
    big = "x" * 50_000
    safe = _safe_jsonish({"s": big}, max_str=10_000)
    assert isinstance(safe["s"], str)
    assert safe["s"].endswith("...<truncated>")
    assert len(safe["s"]) <= 10_000 + len("...<truncated>")
