from __future__ import annotations

"""OOXML Power Query extractor for `xl/queries/*.xml`."""

import hashlib
import re
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from excelminer.backends.base import AnalysisContext, BackendReport
from excelminer.backends.ooxml_zip import (
    OOXMLZipContext,
    _is_ooxml_excel_names,
    _localname,
    _parse_connections_xml,
)
from excelminer.model.entities import MScript, PowerQuery, Source
from excelminer.model.graph import WorkbookGraph
from excelminer.model.normalize import normalize_source_key

_M_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "File.Contents",
        re.compile(r"File\.Contents\s*\(\s*\"([^\"]+)\"\s*\)", re.IGNORECASE),
    ),
    (
        "Folder.Files",
        re.compile(r"Folder\.Files\s*\(\s*\"([^\"]+)\"\s*\)", re.IGNORECASE),
    ),
    (
        "Web.Contents",
        re.compile(r"Web\.Contents\s*\(\s*\"([^\"]+)\"\s*\)", re.IGNORECASE),
    ),
    (
        "SharePoint.Files",
        re.compile(r"SharePoint\.Files\s*\(\s*\"([^\"]+)\"\s*\)", re.IGNORECASE),
    ),
    (
        "Sql.Database",
        re.compile(
            r"Sql\.Database\s*\(\s*\"([^\"]+)\"\s*,\s*\"([^\"]+)\"\s*\)", re.IGNORECASE
        ),
    ),
    (
        "Sql.Databases",
        re.compile(r"Sql\.Databases\s*\(\s*\"([^\"]+)\"\s*\)", re.IGNORECASE),
    ),
    (
        "Odbc.DataSource",
        re.compile(r"Odbc\.DataSource\s*\(\s*\"([^\"]+)\"\s*\)", re.IGNORECASE),
    ),
    (
        "Oracle.Database",
        re.compile(r"Oracle\.Database\s*\(\s*\"([^\"]+)\"\s*\)", re.IGNORECASE),
    ),
    (
        "PostgreSQL.Database",
        re.compile(
            r"PostgreSQL\.Database\s*\(\s*\"([^\"]+)\"\s*,\s*\"([^\"]+)\"\s*\)",
            re.IGNORECASE,
        ),
    ),
]


def _slug(s: str) -> str:
    """Normalize strings for stable keying."""
    return re.sub(r"\s+", " ", (s or "").strip())


def _parse_m_sources(m_code: str) -> list[dict[str, Any]]:
    """Extract data source calls from Power Query (M) code snippets."""
    found: list[dict[str, Any]] = []
    seen: set[tuple[str, ...]] = set()
    if not m_code:
        return found

    for kind, rx in _M_PATTERNS:
        for m in rx.finditer(m_code):
            if kind in ("Sql.Database", "PostgreSQL.Database"):
                server, db = m.group(1).strip(), m.group(2).strip()
                key = (kind, server, db)
                if key in seen:
                    continue
                seen.add(key)
                found.append({"type": kind, "server": server, "database": db})
            else:
                val = m.group(1).strip()
                key = (kind, val)
                if key in seen:
                    continue
                seen.add(key)
                found.append({"type": kind, "value": val})

    return found


def _source_from_m(
    m: dict[str, Any],
) -> tuple[str, str | None, str | None, str | None, str | None]:
    """Return (source_type, server, database, value, provider)."""

    t = str(m.get("type") or "")
    server = m.get("server")
    database = m.get("database")
    value = m.get("value")

    if t in ("Sql.Database", "Sql.Databases"):
        return (
            "sqlserver",
            str(server) if server else (str(value) if value else None),
            str(database) if database else None,
            None,
            t,
        )
    if t == "PostgreSQL.Database":
        return (
            "postgresql",
            str(server) if server else None,
            str(database) if database else None,
            None,
            t,
        )
    if t == "Oracle.Database":
        return "oracle", None, None, str(value) if value else None, t
    if t == "Odbc.DataSource":
        return "odbc_dsn", None, None, str(value) if value else None, t
    if t in ("Web.Contents",):
        return "web", None, None, str(value) if value else None, t
    if t in ("File.Contents", "Folder.Files"):
        return "file", None, None, str(value) if value else None, t
    if t in ("SharePoint.Files",):
        return "sharepoint", None, None, str(value) if value else None, t

    return "unknown", None, None, str(value) if value else None, t or None


def _source_key(
    source_type: str, server: str | None, database: str | None, value: str | None
) -> str:
    """Create a stable key for Source entities."""
    parts = [source_type]
    if server:
        parts.append(server)
    if database:
        parts.append(database)
    if value:
        parts.append(value)
    return "|".join(parts)


def _detect_mashup_parts(
    zf: zipfile.ZipFile, zip_ctx: OOXMLZipContext
) -> list[dict[str, Any]]:
    """Detect Power Query "mashup container" parts.

    Excel can embed Power Query definitions in binary parts rather than `xl/queries/*.xml`.
    We keep this best-effort: report which parts exist and their sizes, without attempting
    to decode proprietary binary formats.
    """

    hits: list[dict[str, Any]] = []
    for name in zip_ctx.namelist(zf):
        lower = name.lower()
        if lower == "xl/mashup/mashup.bin" or lower.startswith("xl/mashup/"):
            try:
                info = zf.getinfo(name)
                hits.append(
                    {"part": name, "size": int(getattr(info, "file_size", 0) or 0)}
                )
            except KeyError:
                continue
        elif lower.startswith("xl/customdata/") and (
            lower.endswith(".data") or lower.endswith(".xml")
        ):
            try:
                info = zf.getinfo(name)
                hits.append(
                    {"part": name, "size": int(getattr(info, "file_size", 0) or 0)}
                )
            except KeyError:
                continue

    # Deduplicate and keep deterministic ordering.
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for h in sorted(hits, key=lambda d: str(d.get("part") or "")):
        p = str(h.get("part") or "")
        if not p or p in seen:
            continue
        seen.add(p)
        out.append(h)
    return out


def _stable_hash(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8"), usedforsecurity=False).hexdigest()


def _extract_mashup_scripts(mashup_bytes: bytes) -> list[dict[str, str]]:
    """Extract M scripts from mashup binaries using a simple heuristic.

    The Mashup binary is a container format that can include multiple scripts.
    We scan for UTF-8 text between `section` and the next `section` boundary
    (or EOF), then split off a name if present.
    """

    if not mashup_bytes:
        return []

    try:
        text = mashup_bytes.decode("utf-8", errors="ignore")
    except Exception:  # noqa: BLE001
        return []

    hits: list[dict[str, str]] = []
    for match in re.finditer(r"section\s+", text, flags=re.IGNORECASE):
        start = match.start()
        next_match = re.search(
            r"(?i)\bsection\s+", text[start + 7 :], flags=re.IGNORECASE
        )
        end = start + 7 + next_match.start() if next_match else len(text)
        chunk = text[start:end].strip()
        if not chunk:
            continue

        name = "MashupSection"
        name_match = re.match(r"(?i)section\s+([A-Za-z0-9_]+)\s*;", chunk)
        if name_match:
            name = name_match.group(1)

        hits.append({"name": name, "m_code": chunk})

    return hits


@dataclass(slots=True)
class PowerQueryZipBackend:
    """Extract Power Query queries from OOXML (`xl/queries/*.xml`).

    Notes:
    - This is a best-effort parser. Some workbooks may store query definitions in
      other locations or require COM automation to access.
    - M code can be large; disable with `include_powerquery=False` if undesired.
    """

    name: str = "powerquery_zip"

    def can_handle(self, ctx: AnalysisContext) -> bool:
        """Return True when Power Query parsing is enabled and available."""
        p = ctx.path
        if not ctx.options.include_powerquery:
            return False
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
        """Extract Power Query metadata and associated sources from OOXML."""
        report = BackendReport(backend=self.name)
        p: Path = ctx.path
        zip_ctx = zip_ctx or OOXMLZipContext.from_path(p)

        queries = 0
        sources = 0
        mashup_queries = 0
        mashup_scripts = 0

        try:
            with zipfile.ZipFile(p) as zf:
                if not _is_ooxml_excel_names(zip_ctx.names_set(zf)):
                    report.add_issue("not an OOXML Excel workbook", kind="unsupported")
                    report.stats = graph.stats()
                    return report

                has_queries_xml = False
                for name in zip_ctx.namelist(zf):
                    if not name.startswith("xl/queries/") or not name.endswith(".xml"):
                        continue

                    has_queries_xml = True

                    data = zip_ctx.read_member(name, zf=zf)
                    if not data:
                        continue

                    try:
                        root = ET.fromstring(data)
                    except ET.ParseError:
                        continue

                    qname = (root.attrib.get("name") or "").strip()
                    if not qname:
                        for el in root.iter():
                            if "name" in el.attrib and el.attrib.get("name"):
                                qname = str(el.attrib.get("name")).strip()
                                break
                    if not qname:
                        qname = Path(name).stem

                    scripts: list[str] = []
                    script_names: list[str] = []
                    for el in root.iter():
                        if _localname(el.tag).lower() == "script" and el.text:
                            scripts.append(el.text)
                            script_names.append(
                                (el.attrib.get("name") or "").strip()
                                if hasattr(el, "attrib")
                                else ""
                            )
                    m_code = "\n".join(scripts).strip() if scripts else ""

                    key = _slug(qname)
                    pq = PowerQuery.make(
                        key=key,
                        id=f"pq:{key}",
                        name=qname,
                        m_code=m_code or None,
                        script_count=len(scripts) or None,
                        script_names=[s for s in script_names if s] or None,
                        extra={"ooxml_part": name} if name else None,
                    )
                    pq_node = graph.upsert(pq)
                    queries += 1

                    for idx, script in enumerate(scripts, start=1):
                        script_name = (
                            script_names[idx - 1]
                            if idx - 1 < len(script_names) and script_names[idx - 1]
                            else f"{qname} Script {idx}"
                        )
                        s_key = _slug(f"{key}:{script_name}:{_stable_hash(script)}")
                        m_node = graph.upsert(
                            MScript.make(
                                key=s_key,
                                id=f"m_script:{s_key}",
                                name=script_name,
                                m_code=script,
                                extra={"ooxml_part": name} if name else None,
                            )
                        )
                        graph.add_edge(pq_node.id, m_node.id, "has_script")

                    for m in _parse_m_sources(m_code):
                        src_type, server, database, value, provider = _source_from_m(m)
                        skey = normalize_source_key(
                            _source_key(src_type, server, database, value)
                        )
                        s = Source.make(
                            source_type=src_type,  # type: ignore[arg-type]
                            key=skey,
                            id=f"src:{skey}",
                            server=server,
                            database=database,
                            value=value,
                            provider=provider,
                        )
                        s_node = graph.upsert(s)
                        graph.add_edge(pq_node.id, s_node.id, "uses_source")
                        sources += 1

                # --- Mashup containers (best-effort) ---
                # Some workbooks store Power Query definitions in binary parts and do not
                # include `xl/queries/*.xml`. In that case, emit a synthetic PowerQuery node
                # so downstream systems can see that Power Query exists.
                mashup_parts = _detect_mashup_parts(zf, zip_ctx)

                # Also detect Mashup connections. This helps for workbooks that have a Mashup
                # connection but no visible queries XML.
                conn_id_to_node_id: dict[str, str] = {}
                for n in graph.nodes.values():
                    if n.kind != "connection":
                        continue
                    cid = str(n.attrs.get("connection_id") or "").strip()
                    if cid:
                        conn_id_to_node_id[cid] = n.id

                mashup_conn_ids: list[str] = []
                mashup_conn_names: list[str] = []
                conns_xml = zip_ctx.connections_xml(zf)

                for c in _parse_connections_xml(conns_xml or b""):
                    raw = str(c.get("connection") or "")
                    if "microsoft.mashup.oledb.1" not in raw.lower():
                        continue
                    cid = str(c.get("id") or "").strip()
                    if cid:
                        mashup_conn_ids.append(cid)
                    name = str(c.get("name") or "").strip()
                    if name:
                        mashup_conn_names.append(name)

                mashup_scripts_found: list[dict[str, str]] = []
                if mashup_parts:
                    for part in mashup_parts:
                        if (
                            str(part.get("part") or "").lower()
                            != "xl/mashup/mashup.bin"
                        ):
                            continue
                        data = zip_ctx.read_member(str(part.get("part")), zf=zf)
                        if not data:
                            continue
                        mashup_scripts_found = _extract_mashup_scripts(data)
                        if mashup_scripts_found:
                            break

                if (mashup_parts or mashup_conn_ids) and not has_queries_xml:
                    name = mashup_conn_names[0] if mashup_conn_names else "Mashup"
                    key = _slug(name) or "mashup"
                    pq = PowerQuery.make(
                        key=key,
                        id=f"pq:{key}",
                        name=name,
                        m_code=None,
                        script_count=len(mashup_scripts_found) or None,
                        script_names=[
                            s.get("name", "")
                            for s in mashup_scripts_found
                            if s.get("name")
                        ]
                        or None,
                        extra={
                            "mashup_container": True,
                            "mashup_parts": mashup_parts,
                            "mashup_connection_ids": sorted(set(mashup_conn_ids)),
                        },
                    )
                    pq_node = graph.upsert(pq)
                    mashup_queries += 1

                    # Link to existing connection nodes (OOXML backend runs earlier by default)
                    for cid in sorted(set(mashup_conn_ids)):
                        node_id = conn_id_to_node_id.get(cid)
                        if node_id:
                            graph.add_edge(pq_node.id, node_id, "uses_connection")

                    for script in mashup_scripts_found:
                        script_name = script.get("name") or "MashupScript"
                        s_key = _slug(
                            f"{key}:{script_name}:{_stable_hash(script.get('m_code') or '')}"
                        )
                        m_node = graph.upsert(
                            MScript.make(
                                key=s_key,
                                id=f"m_script:{s_key}",
                                name=script_name,
                                m_code=script.get("m_code"),
                                extra={"mashup_part": "xl/mashup/mashup.bin"},
                            )
                        )
                        graph.add_edge(pq_node.id, m_node.id, "has_script")
                        mashup_scripts += 1

        except Exception as e:  # noqa: BLE001
            report.add_issue(str(e), kind="runtime")

        report.stats = {
            "power_queries": queries,
            "power_query_sources": sources,
            "power_query_mashup_containers": mashup_queries,
            "power_query_mashup_scripts": mashup_scripts,
            **graph.stats(),
        }
        return report
