from __future__ import annotations

"""Excel COM automation backend (Windows-only, opt-in)."""

import platform
from dataclasses import dataclass
from typing import Any, Mapping

from excelminer.backends.base import AnalysisContext, BackendReport
from excelminer.backends.ooxml_zip import (
    _parse_kv_connection_string,
    _sanitize_kv,
    _source_id,
    _source_key,
    _summarize_conn_kv,
)
from excelminer.model.entities import (
    Connection,
    DefinedName,
    FormulaCell,
    Sheet,
    Source,
)
from excelminer.model.graph import WorkbookGraph
from excelminer.model.normalize import normalize_connection_key, normalize_source_key


def _is_probably_com_proxy(obj: Any) -> bool:
    """Best-effort detection of pywin32 COM proxy objects.

    We avoid importing win32com types here so the module remains importable
    on non-Windows hosts and in minimal test environments.
    """

    if obj is None:
        return False

    # Common pywin32 proxy attribute.
    if hasattr(obj, "_oleobj_"):
        return True

    t = type(obj)
    mod = getattr(t, "__module__", "") or ""
    name = getattr(t, "__name__", "") or ""
    if "win32com" in mod or "pywintypes" in mod:
        return True
    if "CDispatch" in name:
        return True

    return False


def _safe_jsonish(
    value: Any,
    *,
    max_depth: int = 6,
    max_items: int = 200,
    max_str: int = 20_000,
) -> Any:
    """Coerce values into JSON-ish primitives and bound size.

    Primary goal: never allow COM proxies to leak into node attrs.
    Secondary goal: prevent massive notebook outputs from huge strings/arrays.
    """

    if max_depth <= 0:
        return "<max_depth>"

    if _is_probably_com_proxy(value):
        return f"<com:{type(value).__name__}>"

    if value is None or isinstance(value, (bool, int, float)):
        return value

    if isinstance(value, str):
        if len(value) > max_str:
            return value[:max_str] + "...<truncated>"
        return value

    if isinstance(value, (bytes, bytearray)):
        b = bytes(value)
        if len(b) > 1024:
            return f"<bytes:{len(b)}>"
        return b.hex()

    if isinstance(value, Mapping):
        out: dict[str, Any] = {}
        for i, (k, v) in enumerate(value.items()):
            if i >= max_items:
                out["<truncated>"] = f"<items:{len(value)}>"
                break
            out[str(k)] = _safe_jsonish(
                v, max_depth=max_depth - 1, max_items=max_items, max_str=max_str
            )
        return out

    if isinstance(value, (list, tuple, set)):
        seq = list(value)
        if len(seq) > max_items:
            seq = seq[:max_items] + [f"<truncated items:{len(value)}>"]
        return [
            _safe_jsonish(
                v, max_depth=max_depth - 1, max_items=max_items, max_str=max_str
            )
            for v in seq
        ]

    s = str(value)
    if len(s) > max_str:
        s = s[:max_str] + "...<truncated>"
    return s


def _safe_dict(d: dict[str, Any]) -> dict[str, Any]:
    """Normalize dict-like payloads into JSON-friendly primitives."""
    safe = _safe_jsonish(d)
    return safe if isinstance(safe, dict) else {"value": safe}


def _safe_str(s: str | None, *, max_len: int = 20_000) -> str | None:
    """Return a truncated string safe for JSON serialization."""
    if s is None:
        return None
    if len(s) > max_len:
        return s[:max_len] + "...<truncated>"
    return s


def _extract_command_details(conn: Any) -> dict[str, Any]:
    """Extract command text/type/parameters from a connection object."""
    details: dict[str, Any] = {}

    def _try_str(obj: Any, attr: str) -> str | None:
        try:
            v = getattr(obj, attr)
        except Exception:
            return None
        try:
            return str(v).strip() or None
        except Exception:
            return None

    def _extract_params(obj: Any) -> list[dict[str, Any]]:
        params: list[dict[str, Any]] = []
        try:
            param_obj = getattr(obj, "Parameters")
        except Exception:
            return params

        try:
            count = int(getattr(param_obj, "Count", 0) or 0)
        except Exception:
            count = 0

        for i in range(1, count + 1):
            try:
                param = param_obj.Item(i)
            except Exception:
                try:
                    param = param_obj[i]
                except Exception:
                    continue
            name = _try_str(param, "Name") or f"param_{i}"
            value: Any
            try:
                value = getattr(param, "Value")
            except Exception:
                value = None
            params.append({"name": name, "value": _safe_jsonish(value)})
        return params

    targets = [conn]
    try:
        targets.append(getattr(conn, "OLEDBConnection"))
    except Exception:
        pass
    try:
        targets.append(getattr(conn, "ODBCConnection"))
    except Exception:
        pass

    for target in targets:
        if target is None:
            continue
        cmd_text = _try_str(target, "CommandText")
        cmd_type = _try_str(target, "CommandType")
        if cmd_text and "command_text" not in details:
            details["command_text"] = _safe_str(cmd_text)
        if cmd_type and "command_type" not in details:
            details["command_type"] = cmd_type
        if "command_parameters" not in details:
            params = _extract_params(target)
            if params:
                details["command_parameters"] = params

    return details


@dataclass(slots=True)
class ComBackend:
    """Windows-only enrichment backend using Excel COM automation.

    In v0.0.0 this is a safe placeholder. It is wired so callers can opt-in later
    without changing the orchestrator.

    Install extras with: `pip install excelminer[com]`
    """

    name: str = "com"

    def can_handle(self, ctx: AnalysisContext) -> bool:
        """Return True when COM automation is available and permitted."""
        if platform.system() != "Windows":
            return False
        p = ctx.path
        if not p.exists() or not p.is_file():
            return False
        ext = p.suffix.lower()
        # Always allow COM for legacy formats (OOXML parsing may be incomplete or unavailable).
        if ext in (".xls", ".xlsb", ".xlt"):
            return True

        # For modern OOXML files, require explicit opt-in.
        if not getattr(ctx.options, "include_com", False):
            return False

        return ext in (".xlsx", ".xlsm", ".xltx", ".xltm")

    def extract(self, ctx: AnalysisContext, graph: WorkbookGraph) -> BackendReport:
        """Extract workbook artifacts via Excel COM automation."""
        report = BackendReport(backend=self.name)
        try:
            import win32com.client  # type: ignore[import-not-found]
        except Exception as e:  # noqa: BLE001
            report.add_issue(f"pywin32 not available: {e}", kind="dependency")
            report.stats = graph.stats()
            return report

        pythoncom = None
        com_initialized = False
        try:
            import pythoncom  # type: ignore[import-not-found]

            # Ensure COM is initialized for this thread (pytest can run in different contexts).
            pythoncom.CoInitialize()
            com_initialized = True
        except Exception:
            # If pythoncom is unavailable or initialization fails, continue; COM calls may still work.
            pythoncom = None

        xl = None
        wb = None

        # Excel constants (avoid importing win32com.client.constants for speed/reliability)
        msoAutomationSecurityForceDisable = 3

        def _col_to_name(col: int) -> str:
            """Convert 1-indexed column index to Excel column letters."""
            # 1-indexed
            name = ""
            while col > 0:
                col, rem = divmod(col - 1, 26)
                name = chr(65 + rem) + name
            return name

        try:
            xl = win32com.client.DispatchEx("Excel.Application")
            xl.Visible = False
            xl.DisplayAlerts = False
            try:
                xl.AutomationSecurity = msoAutomationSecurityForceDisable
            except Exception:
                # Not available in some Excel versions.
                pass

            # Open workbook read-only; don't update links.
            wb = xl.Workbooks.Open(
                str(ctx.path),
                UpdateLinks=0,
                ReadOnly=True,
                AddToMru=False,
            )

            # --- Sheets ---
            sheets_scanned = 0
            for ws in wb.Worksheets:
                sheets_scanned += 1
                if (
                    ctx.options.max_sheets is not None
                    and sheets_scanned > ctx.options.max_sheets
                ):
                    break

                name = str(ws.Name)
                sheet_key = " ".join(name.strip().split())
                sheet_id = f"sheet:{sheet_key}"
                graph.upsert(
                    Sheet.make(
                        key=sheet_key, id=sheet_id, name=name, index=sheets_scanned
                    )
                )

            # --- Defined names ---
            if ctx.options.include_defined_names:
                try:
                    for n in wb.Names:
                        full_name = str(n.Name)
                        refers_to = _safe_str(str(getattr(n, "RefersTo", "") or ""))

                        scope = "workbook"
                        name = full_name
                        if "!" in full_name:
                            scope, name = full_name.split("!", 1)
                            scope = scope.strip("'")

                        key = f"{scope}|{name}"
                        dn = DefinedName.make(
                            key=key,
                            id=f"defined:{key}",
                            name=name,
                            scope=scope,
                            refers_to=refers_to or "",
                        )
                        dn_node = graph.upsert(dn)
                        if scope not in ("workbook", ""):
                            sheet = graph.get_by_key(
                                "sheet", " ".join(scope.strip().split())
                            )
                            if sheet:
                                graph.add_edge(dn_node.id, sheet.id, "scoped_to")
                except Exception as e:  # noqa: BLE001
                    report.add_issue(
                        f"defined names extraction failed: {e}", kind="runtime"
                    )

            # --- Connections ---
            if ctx.options.include_connections:
                try:
                    count = int(getattr(wb.Connections, "Count", 0) or 0)
                    for i in range(1, count + 1):
                        conn = wb.Connections.Item(i)
                        conn_name = str(getattr(conn, "Name", f"connection_{i}"))
                        raw = ""
                        details: dict[str, Any] = {}

                        def _try_str(obj: Any, attr: str) -> str | None:
                            """Safely fetch an attribute and cast to string."""
                            try:
                                v = getattr(obj, attr)
                            except Exception:
                                return None
                            try:
                                s = str(v)
                            except Exception:
                                return None
                            return s.strip() or None

                        # Try common sub-objects.
                        try:
                            raw = str(getattr(conn, "OLEDBConnection").Connection)
                            details["connection_kind"] = "oledb"
                        except Exception:
                            try:
                                raw = str(getattr(conn, "ODBCConnection").Connection)
                                details["connection_kind"] = "odbc"
                            except Exception:
                                raw = str(getattr(conn, "Connection", "") or "")
                                details["connection_kind"] = "unknown"

                        # Best-effort hints for non-DB connections.
                        # These are guarded and safe; many connection types won't expose these.
                        try:
                            tc = getattr(conn, "TextConnection")
                            details["source_file"] = _try_str(
                                tc, "TextFile"
                            ) or details.get("source_file")
                            details["source_file"] = _try_str(
                                tc, "TextFilePath"
                            ) or details.get("source_file")
                            raw = _try_str(tc, "Connection") or raw
                            if details.get("source_file"):
                                details.setdefault("connection_kind", "text")
                        except Exception:
                            pass

                        try:
                            wq = getattr(conn, "WebQuery")
                            details["url"] = _try_str(wq, "Url") or details.get("url")
                            raw = _try_str(wq, "Connection") or raw
                            if details.get("url"):
                                details.setdefault("connection_kind", "web")
                        except Exception:
                            pass

                        # Some providers expose connection file paths.
                        try:
                            ole = getattr(conn, "OLEDBConnection")
                            details["odc_file"] = _try_str(
                                ole, "SourceConnectionFile"
                            ) or details.get("odc_file")
                        except Exception:
                            pass

                        # Parse common patterns in raw for text/web.
                        raw_s = (raw or "").strip()
                        if raw_s.lower().startswith("url;"):
                            details.setdefault("connection_kind", "web")
                            details.setdefault("url", raw_s.split(";", 1)[1].strip())
                        if raw_s.lower().startswith("text;"):
                            details.setdefault("connection_kind", "text")
                            details.setdefault(
                                "source_file", raw_s.split(";", 1)[1].strip()
                            )

                        key = normalize_connection_key(f"{conn_name}|{i}")
                        kv = _sanitize_kv(_parse_kv_connection_string(raw))
                        hints: dict[str, Any] = {}
                        if kv and raw:
                            summary, hints = _summarize_conn_kv(kv)
                            details["connection_summary"] = summary
                            details["connection_kv"] = kv

                        details.update(_extract_command_details(conn))

                        # Defensive: ensure we only persist JSON-ish primitives and bound sizes.
                        raw_safe = _safe_str(raw or None)
                        details_safe = _safe_dict(details)

                        conn_node = graph.upsert(
                            Connection.make(
                                key=key,
                                id=f"conn:{key}",
                                name=conn_name,
                                connection_kind=str(details.get("connection_kind", "unknown")),  # type: ignore[arg-type]
                                raw=raw_safe,
                                details=details_safe,
                            )
                        )

                        # If we have URL/file hints, create Source nodes even without a DB string.
                        url = str(details.get("url") or "").strip()
                        if url:
                            src_key = normalize_source_key(
                                _source_key("web", None, None, url)
                            )
                            src_node = graph.upsert(
                                Source.make(
                                    source_type="web",  # type: ignore[arg-type]
                                    key=src_key,
                                    id=_source_id(src_key),
                                    value=url,
                                    provider="com:web",
                                )
                            )
                            graph.add_edge(conn_node.id, src_node.id, "uses_source")

                        source_file = str(details.get("source_file") or "").strip()
                        if source_file:
                            src_key = normalize_source_key(
                                _source_key("file", None, None, source_file)
                            )
                            src_node = graph.upsert(
                                Source.make(
                                    source_type="file",  # type: ignore[arg-type]
                                    key=src_key,
                                    id=_source_id(src_key),
                                    value=source_file,
                                    provider="com:text",
                                )
                            )
                            graph.add_edge(conn_node.id, src_node.id, "uses_source")

                        odc_file = str(details.get("odc_file") or "").strip()
                        if odc_file:
                            src_key = normalize_source_key(
                                _source_key("file", None, None, odc_file)
                            )
                            src_node = graph.upsert(
                                Source.make(
                                    source_type="file",  # type: ignore[arg-type]
                                    key=src_key,
                                    id=_source_id(src_key),
                                    value=odc_file,
                                    provider="com:odc",
                                )
                            )
                            graph.add_edge(conn_node.id, src_node.id, "uses_source")

                        if kv and raw:
                            provider = hints.get("provider")
                            server = hints.get("server")
                            database = hints.get("database")
                            dsn = hints.get("dsn")

                            src_type: str = "unknown"
                            value: str | None = None
                            if dsn:
                                src_type = "odbc_dsn"
                                value = str(dsn)
                            elif provider and "sql" in str(provider).lower():
                                src_type = "sqlserver"
                            elif provider and "oracle" in str(provider).lower():
                                src_type = "oracle"

                            src_key = normalize_source_key(
                                _source_key(
                                    src_type,
                                    str(server) if server else None,
                                    str(database) if database else None,
                                    str(value) if value else None,
                                )
                            )
                            src_node = graph.upsert(
                                Source.make(
                                    source_type=src_type,  # type: ignore[arg-type]
                                    key=src_key,
                                    id=_source_id(src_key),
                                    server=str(server) if server else None,
                                    database=str(database) if database else None,
                                    value=value,
                                    provider=str(provider) if provider else None,
                                )
                            )
                            graph.add_edge(conn_node.id, src_node.id, "uses_source")
                except Exception as e:  # noqa: BLE001
                    report.add_issue(
                        f"connections extraction failed: {e}", kind="runtime"
                    )

            # --- Formulas ---
            if ctx.options.include_formulas:
                max_cells = (
                    ctx.options.max_cells_per_sheet
                    if ctx.options.max_cells_per_sheet is not None
                    else 20000
                )
                for ws in wb.Worksheets:
                    sheet_name = str(ws.Name)
                    sheet_key = " ".join(sheet_name.strip().split())
                    sheet = graph.get_by_key("sheet", sheet_key)
                    if not sheet:
                        sheet = graph.upsert(
                            Sheet.make(
                                key=sheet_key, id=f"sheet:{sheet_key}", name=sheet_name
                            )
                        )

                    try:
                        used = ws.UsedRange
                    except Exception:
                        continue

                    scanned = 0
                    try:
                        top = int(getattr(used, "Row", 1) or 1)
                        left = int(getattr(used, "Column", 1) or 1)
                        rows = int(
                            getattr(getattr(used, "Rows", None), "Count", 0) or 0
                        )
                        cols = int(
                            getattr(getattr(used, "Columns", None), "Count", 0) or 0
                        )

                        # Range.Formula returns a scalar for 1x1 or a 2D array for larger ranges.
                        formulas = used.Formula

                        def _iter_cells_formulas() -> list[tuple[int, int, str]]:
                            """Yield (row, col, formula) entries from UsedRange.Formula."""
                            items: list[tuple[int, int, str]] = []
                            if rows <= 0 or cols <= 0:
                                return items

                            # Normalize to 2D array shape.
                            if rows == 1 and cols == 1:
                                val = formulas
                                if isinstance(val, str) and val.startswith("="):
                                    items.append((top, left, val))
                                return items

                            for r_idx, row_vals in enumerate(formulas, start=0):
                                # pywin32 may give a tuple for each row
                                for c_idx, val in enumerate(row_vals, start=0):
                                    if not isinstance(val, str) or not val.startswith(
                                        "="
                                    ):
                                        continue
                                    items.append((top + r_idx, left + c_idx, val))
                            return items

                        for r, c, formula in _iter_cells_formulas():
                            scanned += 1
                            if scanned > max_cells:
                                report.add_issue(
                                    f"{sheet_name}: truncated formulas to {max_cells}",
                                    kind="runtime",
                                )
                                break
                            addr = f"{_col_to_name(c)}{r}"
                            key = f"{sheet_name}!{addr}"
                            node = graph.upsert(
                                FormulaCell.make(
                                    key=key,
                                    id=f"formula:{key}",
                                    sheet_name=sheet_name,
                                    address=addr,
                                    formula=formula,
                                )
                            )
                            graph.add_edge(sheet.id, node.id, "contains")
                    except Exception as e:  # noqa: BLE001
                        report.add_issue(
                            f"{sheet_name}: formula scan failed: {e}",
                            kind="runtime",
                        )

            report.stats = graph.stats()
            return report

        except Exception as e:  # noqa: BLE001
            report.add_issue(f"excel com extraction failed: {e}", kind="runtime")
            report.stats = graph.stats()
            return report

        finally:
            try:
                if wb is not None:
                    wb.Close(SaveChanges=False)
            except Exception:
                pass
            try:
                if xl is not None:
                    xl.Quit()
            except Exception:
                pass

            try:
                if pythoncom is not None and com_initialized:
                    pythoncom.CoUninitialize()
            except Exception:
                pass
