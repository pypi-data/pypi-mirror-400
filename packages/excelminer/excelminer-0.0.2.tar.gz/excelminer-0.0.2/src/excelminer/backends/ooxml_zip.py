from __future__ import annotations

"""OOXML structural extractor (sheets, defined names, connections, sources)."""

import re
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from excelminer.backends.base import AnalysisContext, BackendReport
from excelminer.model.entities import Chart, Connection, DefinedName, Sheet, Source
from excelminer.model.graph import WorkbookGraph
from excelminer.model.normalize import normalize_connection_key, normalize_source_key


def _read_zip_member(zf: zipfile.ZipFile, name: str) -> bytes | None:
    """Read a zip member safely, returning None if it does not exist."""
    try:
        with zf.open(name) as f:
            return f.read()
    except KeyError:
        return None


@dataclass(slots=True)
class OOXMLZipContext:
    """Shared OOXML zip context with cached part contents."""

    path: Path
    _names: list[str] | None = None
    _names_set: set[str] | None = None
    _workbook_xml: bytes | None = None
    _workbook_rels: bytes | None = None
    _connections_xml: bytes | None = None
    _part_cache: dict[str, bytes] = field(default_factory=dict)

    @classmethod
    def from_path(cls, path: Path) -> "OOXMLZipContext":
        """Create a context from a workbook path."""
        return cls(path=path)

    def namelist(self, zf: zipfile.ZipFile | None = None) -> list[str]:
        """Return cached namelist for the zip file."""
        if self._names is None:
            if zf is None:
                with zipfile.ZipFile(self.path) as inner:
                    self._names = inner.namelist()
            else:
                self._names = zf.namelist()
            self._names_set = set(self._names)
        return list(self._names)

    def names_set(self, zf: zipfile.ZipFile | None = None) -> set[str]:
        """Return cached namelist as a set."""
        if self._names_set is None:
            self.namelist(zf)
        return set(self._names_set or set())

    def read_member(
        self, name: str, *, zf: zipfile.ZipFile | None = None, cache: bool = False
    ) -> bytes | None:
        """Read a zip member, optionally caching the bytes."""
        if cache and name in self._part_cache:
            return self._part_cache[name]
        if zf is None:
            with zipfile.ZipFile(self.path) as inner:
                data = _read_zip_member(inner, name)
        else:
            data = _read_zip_member(zf, name)
        if cache and data is not None:
            self._part_cache[name] = data
        return data

    def workbook_xml(self, zf: zipfile.ZipFile | None = None) -> bytes:
        """Return cached workbook.xml bytes."""
        if self._workbook_xml is None:
            self._workbook_xml = (
                self.read_member("xl/workbook.xml", zf=zf, cache=True) or b""
            )
        return self._workbook_xml

    def workbook_rels_xml(self, zf: zipfile.ZipFile | None = None) -> bytes:
        """Return cached workbook.xml.rels bytes."""
        if self._workbook_rels is None:
            self._workbook_rels = (
                self.read_member("xl/_rels/workbook.xml.rels", zf=zf, cache=True) or b""
            )
        return self._workbook_rels

    def connections_xml(self, zf: zipfile.ZipFile | None = None) -> bytes:
        """Return cached connections.xml bytes."""
        if self._connections_xml is None:
            self._connections_xml = (
                self.read_member("xl/connections.xml", zf=zf, cache=True) or b""
            )
        return self._connections_xml


def _localname(tag: str) -> str:
    """Strip XML namespace from a tag and return its local name."""
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


_SENSITIVE_KEYS = {"password", "pwd", "user id", "uid"}


def _split_conn_parts(s: str) -> list[str]:
    """Split connection strings on semicolons, honoring quotes/braces."""
    if not s:
        return []
    parts: list[str] = []
    buf: list[str] = []
    in_quote: str | None = None
    brace_depth = 0

    for ch in s:
        if ch in {"'", '"'}:
            if in_quote == ch:
                in_quote = None
            elif in_quote is None:
                in_quote = ch
        elif ch == "{" and in_quote is None:
            brace_depth += 1
        elif ch == "}" and in_quote is None and brace_depth > 0:
            brace_depth -= 1

        if ch == ";" and in_quote is None and brace_depth == 0:
            part = "".join(buf).strip()
            if part:
                parts.append(part)
            buf = []
            continue
        buf.append(ch)

    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)
    return parts


def _strip_wrapping(value: str) -> str:
    """Strip wrapping quotes/braces from a value."""
    if not value:
        return value
    if len(value) >= 2:
        if (value[0] == value[-1]) and value[0] in {'"', "'"}:
            return value[1:-1]
        if value[0] == "{" and value[-1] == "}":
            return value[1:-1]
    return value


def _parse_kv_connection_string(s: str) -> dict[str, str]:
    """Parse semi-colon-delimited key/value connection strings."""
    kv: dict[str, str] = {}
    if not s:
        return kv
    for part in _split_conn_parts(s):
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        k = k.strip().lower()
        v = _strip_wrapping(v.strip())
        if not k:
            continue
        kv[k] = v
    return kv


def _sanitize_kv(kv: dict[str, str]) -> dict[str, str]:
    """Mask sensitive keys in a connection key/value mapping."""
    out: dict[str, str] = {}
    for k, v in kv.items():
        out[k] = "***" if k in _SENSITIVE_KEYS else v
    return out


def _summarize_conn_kv(kv: dict[str, str]) -> tuple[str, dict[str, Any]]:
    """Return (summary_string, structured_hints).

    Keep this stable and non-lossy enough for graph normalization.
    """

    hints: dict[str, Any] = {}
    provider = kv.get("provider")
    dsn = kv.get("dsn")
    server = (
        kv.get("server")
        or kv.get("data source")
        or kv.get("address")
        or kv.get("network address")
    )
    database = kv.get("database") or kv.get("initial catalog")

    if provider:
        hints["provider"] = provider
    if dsn:
        hints["dsn"] = dsn
    if server:
        hints["server"] = server
    if database:
        hints["database"] = database

    parts: list[str] = []
    if dsn:
        parts.append(f"odbc dsn={dsn}")
    if provider and provider.lower() != "microsoft.mashup.oledb.1":
        parts.append(f"provider={provider}")
    if server:
        parts.append(f"server={server}")
    if database:
        parts.append(f"database={database}")
    summary = "; ".join(parts) if parts else "unknown connection"
    return summary, hints


def _is_ooxml_excel_names(names: set[str]) -> bool:
    """Return True if a namelist set appears to be an OOXML Excel workbook."""
    return "[Content_Types].xml" in names and "xl/workbook.xml" in names


def _is_ooxml_excel(zf: zipfile.ZipFile) -> bool:
    """Return True if the zip appears to be an OOXML Excel workbook."""
    return _is_ooxml_excel_names(set(zf.namelist()))


def _parse_workbook_sheets(wb_xml: bytes) -> list[tuple[int, str]]:
    """Returns list[(index, sheet_name)] in workbook order (1-based index)."""

    out: list[tuple[int, str]] = []
    if not wb_xml:
        return out
    try:
        root = ET.fromstring(wb_xml)
    except ET.ParseError:
        return out

    idx = 0
    for el in root.iter():
        if _localname(el.tag) != "sheet":
            continue
        name = el.attrib.get("name")
        if not name:
            continue
        idx += 1
        out.append((idx, name))
    return out


def _parse_defined_names(wb_xml: bytes) -> list[dict[str, str]]:
    """Parses defined names from workbook.xml."""

    names: list[dict[str, str]] = []
    if not wb_xml:
        return names
    try:
        root = ET.fromstring(wb_xml)
    except ET.ParseError:
        return names

    # Build sheetId->name map (for localSheetId scope)
    sheet_map: dict[str, str] = {}
    for el in root.iter():
        if _localname(el.tag) != "sheet":
            continue
        sheet_id = el.attrib.get("sheetId")
        sheet_name = el.attrib.get("name")
        if sheet_id and sheet_name:
            sheet_map[sheet_id] = sheet_name

    for el in root.iter():
        if _localname(el.tag) != "definedName":
            continue
        name = (el.attrib.get("name") or "").strip()
        refers_to = (el.text or "").strip()
        local_sheet_id = (el.attrib.get("localSheetId") or "").strip()

        if not name:
            continue

        scope = "workbook"
        if local_sheet_id and local_sheet_id.isdigit():
            # localSheetId is 0-based index into workbook sheets in practice, but some
            # writers emit sheetId. We keep it best-effort and stable.
            scope = sheet_map.get(
                str(int(local_sheet_id) + 1), f"sheet:{local_sheet_id}"
            )

        names.append({"name": name, "scope": scope, "refers_to": refers_to})

    return names


def _parse_workbook_root(wb_xml: bytes) -> ET.Element | None:
    """Parse workbook.xml to an XML Element or return None on failure."""
    if not wb_xml:
        return None
    try:
        return ET.fromstring(wb_xml)
    except ET.ParseError:
        return None


def _parse_workbook_sheets_from_root(root: ET.Element) -> list[tuple[int, str]]:
    """Parse sheet names from a pre-parsed workbook root element."""
    out: list[tuple[int, str]] = []
    idx = 0
    for el in root.iter():
        if _localname(el.tag) != "sheet":
            continue
        name = el.attrib.get("name")
        if not name:
            continue
        idx += 1
        out.append((idx, name))
    return out


def _parse_defined_names_from_root(root: ET.Element) -> list[dict[str, str]]:
    """Parse defined names from a pre-parsed workbook root element."""
    names: list[dict[str, str]] = []

    # Build sheetId->name map (for localSheetId scope)
    sheet_map: dict[str, str] = {}
    for el in root.iter():
        if _localname(el.tag) != "sheet":
            continue
        sheet_id = el.attrib.get("sheetId")
        sheet_name = el.attrib.get("name")
        if sheet_id and sheet_name:
            sheet_map[sheet_id] = sheet_name

    for el in root.iter():
        if _localname(el.tag) != "definedName":
            continue
        name = (el.attrib.get("name") or "").strip()
        refers_to = (el.text or "").strip()
        local_sheet_id = (el.attrib.get("localSheetId") or "").strip()

        if not name:
            continue

        scope = "workbook"
        if local_sheet_id and local_sheet_id.isdigit():
            # localSheetId is 0-based index into workbook sheets in practice, but some
            # writers emit sheetId. We keep it best-effort and stable.
            scope = sheet_map.get(
                str(int(local_sheet_id) + 1), f"sheet:{local_sheet_id}"
            )

        names.append({"name": name, "scope": scope, "refers_to": refers_to})

    return names


def _parse_connections_xml(xml_bytes: bytes) -> list[dict[str, Any]]:
    """Minimal, robust connection parsing from xl/connections.xml.

    Extracts:
      - id, name, type
      - raw connection string (if present)
      - url/file hints (web/text)
    """

    out: list[dict[str, Any]] = []
    if not xml_bytes:
        return out
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return out

    for conn in root.iter():
        if _localname(conn.tag) != "connection":
            continue

        c: dict[str, Any] = {}
        c["id"] = conn.attrib.get("id") or ""
        c["name"] = conn.attrib.get("name") or c["id"] or "connection"
        c["type"] = conn.attrib.get("type") or ""

        raw: str | None = None
        details: dict[str, Any] = {}

        odc_file = (conn.attrib.get("odcFile") or "").strip()
        if odc_file:
            details["odc_file"] = odc_file

        for child in list(conn):
            ln = _localname(child.tag)
            if ln in {"dbPr", "oledbPr", "odbcPr"}:
                raw = child.attrib.get("connection") or raw
                if child.attrib.get("command"):
                    details["command"] = child.attrib.get("command")
                if child.attrib.get("commandType"):
                    details["command_type"] = child.attrib.get("commandType")
            elif ln == "webPr":
                details["url"] = child.attrib.get("url") or details.get("url")
            elif ln == "textPr":
                details["source_file"] = child.attrib.get("sourceFile") or details.get(
                    "source_file"
                )

        if raw is not None:
            c["connection"] = raw
        if details:
            c["details"] = details

        out.append(c)

    return out


def _parse_external_link_targets(
    zf: zipfile.ZipFile, zip_ctx: OOXMLZipContext
) -> list[dict[str, str]]:
    """Return list of external link targets discovered in xl/externalLinks.

    This captures external workbook/file sources that often don't appear in
    xl/connections.xml.
    """

    hits: list[dict[str, str]] = []
    for part in sorted(zip_ctx.namelist(zf)):
        if not part.startswith("xl/externalLinks/externalLink") or not part.endswith(
            ".xml"
        ):
            continue

        data = zip_ctx.read_member(part, zf=zf)
        if not data:
            continue

        try:
            root = ET.fromstring(data)
        except ET.ParseError:
            continue

        rid = ""
        for el in root.iter():
            if _localname(el.tag) != "externalBook":
                continue
            for k, v in el.attrib.items():
                if k.endswith("}id") or k == "r:id":
                    rid = v
                    break
            if rid:
                break
        if not rid:
            continue

        rels_part = (
            part.replace("xl/externalLinks/", "xl/externalLinks/_rels/") + ".rels"
        )
        rels_data = zip_ctx.read_member(rels_part, zf=zf)
        if not rels_data:
            continue

        try:
            rels_root = ET.fromstring(rels_data)
        except ET.ParseError:
            continue

        target = ""
        for rel in rels_root.iter():
            if _localname(rel.tag) != "Relationship":
                continue
            if (rel.attrib.get("Id") or "") != rid:
                continue
            target = (rel.attrib.get("Target") or "").strip()
            if target:
                break
        if not target:
            continue

        hits.append({"part": part, "target": target})

    return hits


_NAME_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_\.]*")


def _scan_text_for_defined_names(text: str, names_lower: set[str]) -> set[str]:
    """Return set of defined name matches found in a string."""
    if not text or not names_lower:
        return set()
    tokens = {t.lower() for t in _NAME_TOKEN_RE.findall(text)}
    return tokens & names_lower


def _extract_chart_defined_name_refs(
    zf: zipfile.ZipFile, zip_ctx: OOXMLZipContext
) -> list[dict[str, Any]]:
    """Return chart parts with formula strings referencing defined names."""
    hits: list[dict[str, Any]] = []
    for part in sorted(zip_ctx.namelist(zf)):
        if not part.startswith("xl/charts/") or not part.endswith(".xml"):
            continue

        data = zip_ctx.read_member(part, zf=zf)
        if not data:
            continue

        try:
            root = ET.fromstring(data)
        except ET.ParseError:
            continue

        formulas: list[str] = []
        for el in root.iter():
            if _localname(el.tag) != "f":
                continue
            text = (el.text or "").strip()
            if text:
                formulas.append(text)

        if formulas:
            hits.append({"part": part, "formulas": formulas})

    return hits


def _slug(s: str) -> str:
    """Normalize strings for stable keys."""
    return re.sub(r"\s+", " ", (s or "").strip())


def _sheet_key(name: str) -> str:
    """Return a normalized sheet key for deduplication."""
    return _slug(name)


def _sheet_id(name: str) -> str:
    """Return a stable sheet id from a sheet name."""
    return f"sheet:{_sheet_key(name)}"


def _connection_key(name: str, conn_id: str) -> str:
    """Return a stable connection key combining name and id."""
    if conn_id:
        return f"{_slug(name)}|{conn_id}"
    return _slug(name)


def _connection_id(key: str) -> str:
    """Return a stable connection id from its key."""
    return f"conn:{key}"


def _source_key(
    source_type: str, server: str | None, database: str | None, value: str | None
) -> str:
    """Return a stable source key for graph deduplication."""
    parts = [source_type]
    if server:
        parts.append(server)
    if database:
        parts.append(database)
    if value:
        parts.append(value)
    return "|".join(parts)


def _source_id(key: str) -> str:
    """Return a stable source id from its key."""
    return f"src:{key}"


@dataclass(slots=True)
class OOXMLZipBackend:
    """Structural OOXML backend: workbook.xml, connections.xml, defined names."""

    name: str = "ooxml_zip"

    def can_handle(self, ctx: AnalysisContext) -> bool:
        """Return True when the workbook is an OOXML Excel file."""
        p = ctx.path
        if not p.exists() or not p.is_file():
            return False
        if p.suffix.lower() not in (".xlsx", ".xlsm", ".xltx", ".xltm"):
            return False
        try:
            with zipfile.ZipFile(p):
                return True
        except zipfile.BadZipFile:
            return False

    def extract(
        self,
        ctx: AnalysisContext,
        graph: WorkbookGraph,
        zip_ctx: OOXMLZipContext | None = None,
    ) -> BackendReport:
        """Extract sheets, defined names, connections, and sources from OOXML."""
        report = BackendReport(backend=self.name)
        p = ctx.path
        zip_ctx = zip_ctx or OOXMLZipContext.from_path(p)

        try:
            with zipfile.ZipFile(p) as zf:
                if not _is_ooxml_excel_names(zip_ctx.names_set(zf)):
                    report.add_issue("not an OOXML Excel workbook", kind="unsupported")
                    return report

                wb_xml = zip_ctx.workbook_xml(zf)

                wb_root = _parse_workbook_root(wb_xml)
                sheets = (
                    _parse_workbook_sheets_from_root(wb_root)
                    if wb_root is not None
                    else _parse_workbook_sheets(wb_xml)
                )
                if ctx.options.max_sheets is not None:
                    sheets = sheets[: ctx.options.max_sheets]

                sheet_ids: list[str] = []
                for idx, name in sheets:
                    s = Sheet.make(
                        key=_sheet_key(name), id=_sheet_id(name), name=name, index=idx
                    )
                    s2 = graph.upsert(s)
                    sheet_ids.append(s2.id)

                if ctx.options.include_defined_names:
                    defined = (
                        _parse_defined_names_from_root(wb_root)
                        if wb_root is not None
                        else _parse_defined_names(wb_xml)
                    )
                    for dn in defined:
                        name = dn.get("name", "")
                        scope = dn.get("scope", "workbook")
                        refers_to = dn.get("refers_to", "")
                        key = f"{scope}|{name}"
                        ent = DefinedName.make(
                            key=key,
                            id=f"defined:{key}",
                            name=name,
                            scope=scope,
                            refers_to=refers_to,
                        )
                        dn_node = graph.upsert(ent)
                        if scope not in ("workbook", ""):
                            sheet = graph.get_by_key("sheet", _sheet_key(scope))
                            if sheet:
                                graph.add_edge(dn_node.id, sheet.id, "scoped_to")

                    dn_nodes = [
                        n for n in graph.nodes.values() if n.kind == "defined_name"
                    ]
                    name_to_ids: dict[str, list[str]] = {}
                    for n in dn_nodes:
                        nm = str(n.attrs.get("name") or "").strip()
                        if not nm:
                            continue
                        name_to_ids.setdefault(nm.lower(), []).append(n.id)

                    if name_to_ids:
                        names_lower = set(name_to_ids.keys())
                        for hit in _extract_chart_defined_name_refs(zf, zip_ctx):
                            formulas = list(hit.get("formulas") or [])
                            if not formulas:
                                continue
                            used_names: set[str] = set()
                            for formula in formulas:
                                used_names |= _scan_text_for_defined_names(
                                    formula, names_lower
                                )
                            if not used_names:
                                continue

                            part = str(hit.get("part") or "")
                            key = part or "chart"
                            chart_node = graph.upsert(
                                Chart.make(
                                    key=key,
                                    id=f"chart:{key}",
                                    name=Path(part).name or "Chart",
                                    extra={"ooxml_part": part},
                                )
                            )
                            for nm in sorted(used_names):
                                for dn_id in name_to_ids.get(nm, []):
                                    graph.add_edge(
                                        chart_node.id, dn_id, "uses_defined_name"
                                    )

                if ctx.options.include_connections:
                    conns_xml = zip_ctx.connections_xml(zf)
                    for c in _parse_connections_xml(conns_xml or b""):
                        conn_name = str(c.get("name") or "connection")
                        conn_id = str(c.get("id") or "")
                        conn_type = str(c.get("type") or "")
                        raw = str(c.get("connection") or "")
                        details = dict(c.get("details") or {})
                        if conn_id:
                            details.setdefault("connection_id", conn_id)

                        kind = "unknown"
                        if raw.lower().startswith("odbc") or "dsn=" in raw.lower():
                            kind = "odbc"
                        elif "provider=" in raw.lower() or conn_type == "1":
                            kind = "oledb"
                        elif "url" in details:
                            kind = "web"
                        elif "source_file" in details:
                            kind = "text"

                        kv = _parse_kv_connection_string(raw)
                        sanitized = _sanitize_kv(kv)
                        hints: dict[str, Any] = {}
                        if sanitized and raw:
                            summary, hints = _summarize_conn_kv(sanitized)
                            details.setdefault("connection_summary", summary)
                            details.setdefault("connection_kv", sanitized)

                        provider = str(hints.get("provider") or "")
                        if provider.lower() == "microsoft.mashup.oledb.1":
                            kind = "powerquery"

                        key = normalize_connection_key(
                            _connection_key(conn_name, conn_id)
                        )
                        conn = Connection.make(
                            key=key,
                            id=_connection_id(key),
                            name=conn_name,
                            connection_kind=kind,  # type: ignore[arg-type]
                            raw=raw or None,
                            details=details or None,
                        )
                        conn_node = graph.upsert(conn)

                        # Create Source nodes even for non-DB connections.
                        url = str(details.get("url") or "").strip()
                        if url:
                            src_key = normalize_source_key(
                                _source_key("web", None, None, url)
                            )
                            src = Source.make(
                                source_type="web",
                                key=src_key,
                                id=_source_id(src_key),
                                value=url,
                                provider="webPr",
                            )
                            src_node = graph.upsert(src)
                            graph.add_edge(conn_node.id, src_node.id, "uses_source")

                        source_file = str(details.get("source_file") or "").strip()
                        if source_file:
                            src_key = normalize_source_key(
                                _source_key("file", None, None, source_file)
                            )
                            src = Source.make(
                                source_type="file",
                                key=src_key,
                                id=_source_id(src_key),
                                value=source_file,
                                provider="textPr",
                            )
                            src_node = graph.upsert(src)
                            graph.add_edge(conn_node.id, src_node.id, "uses_source")

                        odc_file = str(details.get("odc_file") or "").strip()
                        if odc_file:
                            src_key = normalize_source_key(
                                _source_key("file", None, None, odc_file)
                            )
                            src = Source.make(
                                source_type="file",
                                key=src_key,
                                id=_source_id(src_key),
                                value=odc_file,
                                provider="odcFile",
                            )
                            src_node = graph.upsert(src)
                            graph.add_edge(conn_node.id, src_node.id, "uses_source")

                        if sanitized and raw:
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
                                _source_key(src_type, server, database, value)
                            )
                            src = Source.make(
                                source_type=src_type,  # type: ignore[arg-type]
                                key=src_key,
                                id=_source_id(src_key),
                                server=str(server) if server else None,
                                database=str(database) if database else None,
                                value=value,
                                provider=str(provider) if provider else None,
                            )
                            src_node = graph.upsert(src)
                            graph.add_edge(conn_node.id, src_node.id, "uses_source")

                    # External links are another source of data dependencies.
                    for hit in _parse_external_link_targets(zf, zip_ctx):
                        target = str(hit.get("target") or "").strip()
                        if not target:
                            continue

                        src_type: str = "file"
                        tl = target.lower()
                        if tl.startswith("http://") or tl.startswith("https://"):
                            src_type = "web"

                        src_key = normalize_source_key(
                            _source_key(src_type, None, None, target)
                        )
                        src = Source.make(
                            source_type=src_type,  # type: ignore[arg-type]
                            key=src_key,
                            id=_source_id(src_key),
                            value=target,
                            provider="externalLink",
                            extra={"ooxml_part": str(hit.get("part") or "")},
                        )
                        src_node = graph.upsert(src)

                        ckey = normalize_connection_key(
                            f"{_connection_key('externalLink', '')}|{_slug(target)}"
                        )
                        conn = Connection.make(
                            key=ckey,
                            id=_connection_id(ckey),
                            name="externalLink",
                            connection_kind="unknown",
                            raw=None,
                            details={
                                "external_link_target": target,
                                "external_link_part": str(hit.get("part") or ""),
                            },
                        )
                        conn_node = graph.upsert(conn)
                        graph.add_edge(conn_node.id, src_node.id, "uses_source")

                report.stats = graph.stats()
                report.stats.update({"sheets": len(sheet_ids)})
                return report

        except Exception as e:  # noqa: BLE001
            report.add_issue(str(e), kind="runtime")
            return report
