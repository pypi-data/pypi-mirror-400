from __future__ import annotations

"""Pandas/calamine backend for fast used-range detection."""

from dataclasses import dataclass
from typing import Any

from excelminer.backends.base import AnalysisContext, BackendReport
from excelminer.model.entities import CellBlock, Sheet
from excelminer.model.graph import WorkbookGraph


@dataclass(slots=True)
class CalamineBackend:
    """Fast sheet scanning backend using pandas + engine="calamine".

    This backend is optional in v0.0.0; it is included as a placeholder for future
    CellBlock extraction and large-workbook scanning.

    Install extras with: `pip install excelminer[calamine]`
    """

    name: str = "calamine"

    def can_handle(self, ctx: AnalysisContext) -> bool:
        """Return True when calamine scanning is enabled and supported."""
        p = ctx.path
        if not p.exists() or not p.is_file():
            return False
        if not ctx.options.include_cells:
            return False
        return p.suffix.lower() in (".xlsx", ".xlsm", ".xls", ".ods")

    def extract(self, ctx: AnalysisContext, graph: WorkbookGraph) -> BackendReport:
        """Scan worksheets for used ranges and emit CellBlock nodes."""
        report = BackendReport(backend=self.name)

        try:
            import pandas as pd  # type: ignore[import-not-found]
        except Exception as e:  # noqa: BLE001
            report.add_issue(
                f"pandas not available (install excelminer[calamine]): {e}",
                kind="dependency",
            )
            report.stats = graph.stats()
            return report

        # python-calamine registers itself as a pandas engine.
        try:
            # Validate the engine import path exists; pandas will still resolve by name.
            import python_calamine  # type: ignore[import-not-found]  # noqa: F401
        except Exception as e:  # noqa: BLE001
            report.add_issue(
                f"python-calamine not available (install excelminer[calamine]): {e}",
                kind="dependency",
            )
            report.stats = graph.stats()
            return report

        def col_to_letters(col_1_based: int) -> str:
            """Convert 1-based column index to Excel column letters."""
            # 1 -> A, 26 -> Z, 27 -> AA
            letters: list[str] = []
            n = col_1_based
            while n > 0:
                n, rem = divmod(n - 1, 26)
                letters.append(chr(ord("A") + rem))
            return "".join(reversed(letters))

        def a1_range(r1: int, c1: int, r2: int, c2: int) -> str:
            """Build an A1 notation range string from 1-based indices."""
            return f"{col_to_letters(c1)}{r1}:{col_to_letters(c2)}{r2}"

        def is_na(v: Any) -> bool:
            """Return True if a value should be treated as empty."""
            try:
                # pandas isna covers NaN/NA/NaT.
                return bool(pd.isna(v))
            except Exception:
                return v is None

        blocks = 0
        sheets_scanned = 0

        try:
            excel_file = pd.ExcelFile(ctx.path, engine="calamine")
        except Exception as e:  # noqa: BLE001
            report.add_issue(f"calamine read failed: {e}", kind="parse_error")
            report.stats = graph.stats()
            return report

        try:
            sheet_names = list(getattr(excel_file, "sheet_names", []))
            for sheet_name in sheet_names:
                sheets_scanned += 1
                if (
                    ctx.options.max_sheets is not None
                    and sheets_scanned > ctx.options.max_sheets
                ):
                    break

                try:
                    df: Any = excel_file.parse(
                        sheet_name,
                        header=None,
                        dtype=object,
                    )
                except Exception as e:  # noqa: BLE001
                    report.add_issue(f"calamine read failed: {e}", kind="parse_error")
                    report.stats = graph.stats()
                    return report

                sheet_key = " ".join(str(sheet_name).strip().split())
                sheet_id = f"sheet:{sheet_key}"
                sheet_node = graph.get_by_key("sheet", sheet_key)
                if not sheet_node:
                    sheet_node = graph.upsert(
                        Sheet.make(key=sheet_key, id=sheet_id, name=str(sheet_name))
                    )

                # Determine used range by non-null mask.
                try:
                    mask = df.notna()
                except Exception:
                    # If df is not a DataFrame-like (shouldn't happen), skip.
                    continue

                if mask.values.size == 0:
                    continue

                rows_any = mask.any(axis=1)
                cols_any = mask.any(axis=0)

                if not bool(rows_any.any()) or not bool(cols_any.any()):
                    continue

                # Indices are 0-based.
                used_row_indices = list(rows_any[rows_any].index)
                used_col_indices = [int(c) for c in cols_any[cols_any].index]
                r0 = int(min(used_row_indices))
                r1 = int(max(used_row_indices))
                c0 = int(min(used_col_indices))
                c1 = int(max(used_col_indices))

                # Apply max_cells_per_sheet as a cap on the used-range rectangle.
                max_cells = ctx.options.max_cells_per_sheet
                if max_cells is not None:
                    rect_cells = (r1 - r0 + 1) * (c1 - c0 + 1)
                    if rect_cells > max_cells and (c1 - c0 + 1) > 0:
                        # Reduce row count to fit within max_cells.
                        max_rows = max(1, max_cells // (c1 - c0 + 1))
                        r1 = r0 + max_rows - 1
                        report.add_issue(
                            f"{sheet_name}: truncated used range to max_cells_per_sheet",
                            kind="runtime",
                        )

                r1b, c1b, r2b, c2b = r0 + 1, c0 + 1, r1 + 1, c1 + 1
                rng = a1_range(r1b, c1b, r2b, c2b)

                sub = df.iloc[r0 : r1 + 1, c0 : c1 + 1]
                non_null = int(sub.notna().values.sum())

                # Sample top-left portion.
                sample_df = sub.iloc[
                    : ctx.options.sample_rows_per_block,
                    : ctx.options.sample_cols_per_block,
                ]
                sample: list[list[Any]] = []
                for row in sample_df.itertuples(index=False, name=None):
                    sample.append([None if is_na(v) else v for v in row])

                stats = {
                    "rows": int(r1 - r0 + 1),
                    "cols": int(c1 - c0 + 1),
                    "non_null": non_null,
                }

                key = f"{sheet_key}|{rng}"
                block = CellBlock.make(
                    key=key,
                    id=f"block:{key}",
                    sheet_name=str(sheet_name),
                    a1_range=rng,
                    block_type="value_block",  # type: ignore[arg-type]
                    stats=stats,
                    sample=sample,
                )
                block_node = graph.upsert(block)
                graph.add_edge(sheet_node.id, block_node.id, "contains")
                blocks += 1
        finally:
            close = getattr(excel_file, "close", None)
            if callable(close):
                close()

        report.stats = {
            "sheets_scanned": sheets_scanned,
            "cell_blocks": blocks,
            **graph.stats(),
        }
        return report
