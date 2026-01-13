from __future__ import annotations

"""Public API helpers for analyzing Excel workbooks.

This module orchestrates backend execution and provides dictionary-friendly
serialization helpers for downstream tooling.
"""

from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable, Iterable

from excelminer.backends import (
    AnalysisContext,
    AnalysisOptions,
    Backend,
    BackendReport,
    CalamineBackend,
    ComBackend,
    OOXMLZipBackend,
    OpenpyxlBackend,
    PivotZipBackend,
    PowerQueryZipBackend,
    VbaZipBackend,
)
from excelminer.backends.ooxml_zip import OOXMLZipContext
from excelminer.model.entities import Edge, Entity
from excelminer.model.graph import WorkbookGraph


def _default_backends() -> list[Backend]:
    """Return the default backend execution order.

    The ordering is intentional: structural parsers populate the graph first,
    then semantic scanners enrich it, and OS-specific enrichers run last.
    """

    # Ordered from structural -> semantic -> enrichment.
    return [
        OOXMLZipBackend(),
        VbaZipBackend(),
        PowerQueryZipBackend(),
        PivotZipBackend(),
        CalamineBackend(),
        OpenpyxlBackend(),
        ComBackend(),
    ]


def analyze_workbook(
    path: str | Path,
    *,
    options: AnalysisOptions | None = None,
    backends: Iterable[Backend] | None = None,
    node_sink: Callable[[Entity], None] | None = None,
    edge_sink: Callable[[Edge], None] | None = None,
) -> tuple[WorkbookGraph, list[BackendReport], AnalysisContext]:
    """Analyze an Excel workbook into a graph plus backend reports."""
    ctx = AnalysisContext(path=Path(path), options=options or AnalysisOptions())
    log_callback = ctx.options.log_callback
    graph = WorkbookGraph()
    if node_sink is not None:
        graph.register_node_sink(node_sink)
    if edge_sink is not None:
        graph.register_edge_sink(edge_sink)

    reports: list[BackendReport] = []
    zip_ctx: OOXMLZipContext | None = None
    ooxml_backends = (
        OOXMLZipBackend,
        VbaZipBackend,
        PowerQueryZipBackend,
        PivotZipBackend,
    )
    for backend in (list(backends) if backends is not None else _default_backends()):
        try:
            if not backend.can_handle(ctx):
                continue
            # Each backend appends to the shared graph as it discovers artifacts.
            if isinstance(backend, ooxml_backends):
                if zip_ctx is None:
                    zip_ctx = OOXMLZipContext.from_path(ctx.path)
                report = backend.extract(ctx, graph, zip_ctx=zip_ctx)
            else:
                report = backend.extract(ctx, graph)
        except Exception as e:  # noqa: BLE001
            issue_message = f"backend {getattr(backend, 'name', type(backend).__name__)} failed: {e}"
            ctx.add_issue(issue_message)
            if log_callback is not None:
                log_callback(issue_message)
            report = BackendReport(
                backend=getattr(backend, "name", type(backend).__name__)
            )
            report.add_issue(str(e), kind="runtime")
        reports.append(report)

    if ctx.options.post_analysis_distillation:
        try:
            # Lazy import to avoid circular import when users import
            # excelminer.rationalization.formulas directly.
            from excelminer.rationalization import distill_graph

            reports.append(distill_graph(ctx, graph))
        except Exception as e:  # noqa: BLE001
            issue_message = f"post_analysis_distillation failed: {e}"
            ctx.add_issue(issue_message)
            if log_callback is not None:
                log_callback(issue_message)
            report = BackendReport(backend="distillation")
            report.add_issue(str(e), kind="runtime")
            reports.append(report)

    return graph, reports, ctx


def analyze_to_dict(
    path: str | Path,
    *,
    options: AnalysisOptions | None = None,
    backends: Iterable[Backend] | None = None,
) -> dict[str, Any]:
    """Analyze a workbook and return a JSON-friendly dictionary."""
    graph, reports, ctx = analyze_workbook(path, options=options, backends=backends)
    options_dict = asdict(ctx.options)
    options_dict["log_callback"] = None
    return {
        "path": str(ctx.path),
        "options": options_dict,
        "issues": list(ctx.issues),
        "reports": [asdict(r) for r in reports],
        "graph": graph.to_dict(),
    }
