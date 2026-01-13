from __future__ import annotations

"""Top-level package exports for excelminer."""

from .api import analyze_to_dict, analyze_workbook
from .backends.base import AnalysisContext, AnalysisOptions, Backend, BackendReport
from .backends.pivot_zip import PivotZipBackend
from .backends.powerquery_zip import PowerQueryZipBackend
from .model.graph import WorkbookGraph
from .reporting import (
    list_connections,
    list_sources,
    summarize_connections,
    summarize_sources,
)


def distill_graph(*args, **kwargs):  # type: ignore[no-untyped-def]
    """Lazy proxy for the distillation helper."""
    from .rationalization import distill_graph as _distill_graph

    return _distill_graph(*args, **kwargs)


__version__ = "0.0.2"

__all__ = [
    "__version__",
    "AnalysisContext",
    "AnalysisOptions",
    "Backend",
    "BackendReport",
    "PivotZipBackend",
    "PowerQueryZipBackend",
    "WorkbookGraph",
    "analyze_workbook",
    "analyze_to_dict",
    "distill_graph",
    "list_sources",
    "summarize_sources",
    "list_connections",
    "summarize_connections",
]
