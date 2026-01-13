from __future__ import annotations

"""Core backend contracts and configuration types."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Literal, Protocol

from excelminer.model.graph import WorkbookGraph


@dataclass(slots=True)
class AnalysisOptions:
    """Flags + limits.

    Keep this minimal at first; expand as you add extractors.
    """

    include_vba: bool = True
    include_connections: bool = True
    include_powerquery: bool = True
    include_pivots: bool = True
    include_defined_names: bool = True

    # Explicit opt-in for Excel COM automation (Windows + Excel required)
    include_com: bool = False

    include_cells: bool = False  # value blocks, used ranges
    include_formulas: bool = False  # formula inventory + deps

    # Optional post-processing step to condense/refine extracted artifacts.
    # Disabled by default to preserve existing behavior and output shape.
    post_analysis_distillation: bool = False

    # Limits to keep scans bounded for huge workbooks
    max_sheets: int | None = None
    max_cells_per_sheet: int | None = None
    max_rows_per_sheet: int | None = None
    max_cols_per_sheet: int | None = None
    row_chunk_size: int = 500
    column_chunk_size: int = 50
    sample_rows_per_block: int = 10
    sample_cols_per_block: int = 12
    log_callback: Callable[[str], None] | None = None


@dataclass(slots=True)
class AnalysisContext:
    """Shared analysis context passed to every backend."""

    path: Path
    options: AnalysisOptions = field(default_factory=AnalysisOptions)
    issues: list[str] = field(default_factory=list)

    def add_issue(self, msg: str) -> None:
        """Record a non-fatal issue encountered during analysis."""
        self.issues.append(msg)


@dataclass(slots=True)
class BackendReport:
    """Lightweight report for a backend run."""

    backend: str
    issues: list["Issue"] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)

    def add_issue(
        self,
        message: str,
        *,
        kind: "IssueKind" = "runtime",
        detail: str | None = None,
    ) -> None:
        """Add a structured issue to this report."""
        issue = Issue(kind=kind, message=message, detail=detail)
        self.issues.append(issue)


IssueKind = Literal[
    "dependency",
    "missing_optional",
    "parse_error",
    "runtime",
    "unsupported",
]


@dataclass(slots=True)
class Issue:
    """Structured issue with taxonomy support."""

    kind: IssueKind
    message: str
    detail: str | None = None


class Backend(Protocol):
    """Backend interface.

    A backend may be structural (OOXML parsing), semantic (cell scanning), or
    OS-specific (COM).
    """

    name: str

    def can_handle(self, ctx: AnalysisContext) -> bool: ...

    def extract(self, ctx: AnalysisContext, graph: WorkbookGraph) -> BackendReport: ...


class BackendError(RuntimeError):
    """Raised when a backend cannot continue due to a fatal condition."""
