from __future__ import annotations

"""Rationalization helpers for post-analysis graph refinement."""


def distill_graph(*args, **kwargs):  # type: ignore[no-untyped-def]
    """Proxy to distillation entrypoint to avoid eager imports."""
    from .distill import distill_graph as _distill_graph

    return _distill_graph(*args, **kwargs)


__all__ = ["distill_graph"]
