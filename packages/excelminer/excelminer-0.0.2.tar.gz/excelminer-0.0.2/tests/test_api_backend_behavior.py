from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from excelminer.api import analyze_workbook
from excelminer.backends.base import AnalysisContext, AnalysisOptions, BackendReport
from excelminer.backends.calamine_backend import CalamineBackend
from excelminer.backends.com_backend import ComBackend
from excelminer.model.graph import WorkbookGraph


@dataclass(slots=True)
class _ExplodingBackend:
    name: str = "boom"

    def can_handle(self, ctx: AnalysisContext) -> bool:  # noqa: ARG002
        return True

    def extract(
        self, ctx: AnalysisContext, graph: WorkbookGraph
    ) -> BackendReport:  # noqa: ARG002
        raise RuntimeError("kaboom")


def test_analyze_workbook_catches_backend_exceptions(tmp_path: Path) -> None:
    p = tmp_path / "missing.xlsx"

    graph, reports, ctx = analyze_workbook(
        p,
        options=AnalysisOptions(include_formulas=False, include_cells=False),
        backends=[_ExplodingBackend()],
    )

    assert isinstance(graph, WorkbookGraph)
    assert len(reports) == 1
    assert reports[0].backend == "boom"
    assert reports[0].issues and "kaboom" in reports[0].issues[0].message
    assert ctx.issues and "backend boom failed" in ctx.issues[0]


def test_placeholder_backends_are_gated_by_options_and_deps(tmp_path: Path) -> None:
    # Create a real empty file with supported suffix.
    p = tmp_path / "x.xlsx"
    p.write_bytes(b"dummy")

    # Calamine backend requires include_cells.
    cal = CalamineBackend()
    assert (
        cal.can_handle(
            AnalysisContext(path=p, options=AnalysisOptions(include_cells=False))
        )
        is False
    )
    assert (
        cal.can_handle(
            AnalysisContext(path=p, options=AnalysisOptions(include_cells=True))
        )
        is True
    )

    # COM backend should at least be callable; may be gated by OS.
    com = ComBackend()
    ctx = AnalysisContext(path=p)
    ok = com.can_handle(ctx)
    assert ok in (True, False)

    if ok:
        rep = com.extract(ctx, WorkbookGraph())
        assert rep.backend == "com"
        assert rep.stats


def test_openpyxl_backend_gating(tmp_path: Path) -> None:
    from excelminer.backends.openpyxl_backend import OpenpyxlBackend

    p = tmp_path / "x.xlsx"
    p.write_bytes(b"dummy")

    b = OpenpyxlBackend()
    assert (
        b.can_handle(
            AnalysisContext(
                path=p,
                options=AnalysisOptions(include_formulas=False, include_cells=False),
            )
        )
        is False
    )
    assert (
        b.can_handle(
            AnalysisContext(path=p, options=AnalysisOptions(include_formulas=True))
        )
        is True
    )

    # If we try to extract with a non-xlsx zip, it should report load failure not crash.
    rep = b.extract(
        AnalysisContext(path=p, options=AnalysisOptions(include_formulas=True)),
        WorkbookGraph(),
    )
    assert rep.backend == "openpyxl"
    assert rep.issues
