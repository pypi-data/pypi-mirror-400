from __future__ import annotations

"""OOXML pivot table/cache extractor."""

import os
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
    _sheet_key,
)
from excelminer.model.entities import PivotCache, PivotTable
from excelminer.model.graph import WorkbookGraph


def _get_sheet_path_to_name(
    zf: zipfile.ZipFile, zip_ctx: OOXMLZipContext
) -> dict[str, str]:
    """Return map of full worksheet part path -> sheet name."""

    wb_xml = zip_ctx.workbook_xml(zf)
    wb_rels = zip_ctx.workbook_rels_xml(zf)

    rid_to_target: dict[str, str] = {}
    try:
        root = ET.fromstring(wb_rels)
        for rel in root.iter():
            if _localname(rel.tag) != "Relationship":
                continue
            rid = rel.attrib.get("Id") or ""
            target = rel.attrib.get("Target") or ""
            if not rid or not target:
                continue
            if "worksheets/" in target.replace("\\", "/"):
                rid_to_target[rid] = os.path.normpath(
                    os.path.join("xl", target)
                ).replace("\\", "/")
    except ET.ParseError:
        pass

    sheet_path_to_name: dict[str, str] = {}
    try:
        root = ET.fromstring(wb_xml)
        for el in root.iter():
            if _localname(el.tag) != "sheet":
                continue
            name = (el.attrib.get("name") or "").strip()
            if not name:
                continue

            rid = ""
            for k, v in el.attrib.items():
                if k.endswith("}id") or k == "r:id":
                    rid = v
                    break

            target = rid_to_target.get(rid)
            if target:
                sheet_path_to_name[target] = name
    except ET.ParseError:
        pass

    return sheet_path_to_name


def _get_pivot_table_to_sheet(
    zf: zipfile.ZipFile,
    zip_ctx: OOXMLZipContext,
    sheet_path_to_name: dict[str, str],
) -> dict[str, str]:
    """Map full pivotTable part path -> sheet name."""

    out: dict[str, str] = {}
    for rels_path in zip_ctx.namelist(zf):
        if not rels_path.startswith("xl/worksheets/_rels/") or not rels_path.endswith(
            ".xml.rels"
        ):
            continue

        sheet_path = rels_path.replace(
            "xl/worksheets/_rels/", "xl/worksheets/"
        ).replace(".rels", "")
        sheet_name = sheet_path_to_name.get(sheet_path, "Unknown")

        rels_data = zip_ctx.read_member(rels_path, zf=zf)
        if not rels_data:
            continue

        try:
            root = ET.fromstring(rels_data)
        except ET.ParseError:
            continue

        for rel in root.iter():
            if _localname(rel.tag) != "Relationship":
                continue
            rel_type = rel.attrib.get("Type", "")
            if "pivotTable" not in rel_type:
                continue
            target = rel.attrib.get("Target", "")
            if not target:
                continue

            pt_path = os.path.normpath(os.path.join("xl/worksheets", target)).replace(
                "\\", "/"
            )
            out[pt_path] = sheet_name

    return out


def _get_cache_id_to_rid(
    zf: zipfile.ZipFile, zip_ctx: OOXMLZipContext
) -> dict[str, str]:
    """Map pivot cache IDs to relationship IDs from workbook.xml."""
    cache_id_to_rid: dict[str, str] = {}
    wb_xml = zip_ctx.workbook_xml(zf)
    if not wb_xml:
        return cache_id_to_rid

    try:
        root = ET.fromstring(wb_xml)
    except ET.ParseError:
        return cache_id_to_rid

    for el in root.iter():
        if _localname(el.tag) != "pivotCache":
            continue
        cache_id = (el.attrib.get("cacheId") or "").strip()
        if not cache_id:
            continue
        rid = ""
        for k, v in el.attrib.items():
            if k.endswith("}id") or k == "r:id":
                rid = v
                break
        if rid:
            cache_id_to_rid[cache_id] = rid

    return cache_id_to_rid


def _get_rid_to_cache_def_path(
    zf: zipfile.ZipFile, zip_ctx: OOXMLZipContext
) -> dict[str, str]:
    """Map relationship IDs to cache definition part paths."""
    rid_to_path: dict[str, str] = {}
    rels = zip_ctx.workbook_rels_xml(zf)
    if not rels:
        return rid_to_path

    try:
        root = ET.fromstring(rels)
    except ET.ParseError:
        return rid_to_path

    for rel in root.iter():
        if _localname(rel.tag) != "Relationship":
            continue
        rel_type = rel.attrib.get("Type", "")
        if "pivotCacheDefinition" not in rel_type:
            continue
        rid = rel.attrib.get("Id", "")
        target = rel.attrib.get("Target", "")
        if not rid or not target:
            continue
        rid_to_path[rid] = os.path.normpath(os.path.join("xl", target)).replace(
            "\\", "/"
        )

    return rid_to_path


def _column_letters_to_index(col: str) -> int:
    """Convert column letters to a 1-based index."""
    idx = 0
    for ch in col.upper():
        if not ch.isalpha():
            continue
        idx = idx * 26 + (ord(ch) - ord("A") + 1)
    return idx


def _index_to_column_letters(idx: int) -> str:
    """Convert a 1-based index to column letters."""
    if idx <= 0:
        return ""
    letters = ""
    while idx:
        idx, rem = divmod(idx - 1, 26)
        letters = chr(ord("A") + rem) + letters
    return letters


def _columns_from_ref(ref: str) -> list[str]:
    """Return a list of column letters from an A1-style range ref."""
    if not ref:
        return []
    m = re.search(r"\$?([A-Z]+)\$?\d+(?::\$?([A-Z]+)\$?\d+)?", ref, re.I)
    if not m:
        return []
    start = _column_letters_to_index(m.group(1))
    end = _column_letters_to_index(m.group(2) or m.group(1))
    if start <= 0 or end <= 0:
        return []
    if end < start:
        start, end = end, start
    return [_index_to_column_letters(i) for i in range(start, end + 1)]


def _parse_cache_definition(
    zf: zipfile.ZipFile, zip_ctx: OOXMLZipContext, cache_path: str
) -> tuple[str, str, list[str], dict[str, str], dict[str, str], str]:
    """Return parsed cache metadata (types, references, field mappings)."""

    data = zip_ctx.read_member(cache_path, zf=zf)
    if not data:
        return "unknown", "missing cache definition", [], {}, {}, ""

    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return "unknown", "unparseable cache definition", [], {}, {}, ""

    source_type = "unknown"
    source_ref = "Unknown"
    source_name = ""
    source_sheet = ""
    source_ref_range = ""

    # Parse cache fields
    field_names: list[str] = []
    field_idx_map: dict[str, str] = {}
    for elem in root.iter():
        if _localname(elem.tag) != "cacheFields":
            continue
        idx = 0
        for cf in elem:
            if _localname(cf.tag) != "cacheField":
                continue
            nm = (cf.attrib.get("name") or "").strip()
            if nm:
                field_names.append(nm)
                field_idx_map[str(idx)] = nm
            idx += 1
        break

    # Parse cache source
    for elem in root.iter():
        if _localname(elem.tag) != "cacheSource":
            continue

        conn_id = (elem.attrib.get("connectionId") or "").strip()

        # Prefer explicit children
        for child in list(elem):
            ln = _localname(child.tag)
            if ln == "worksheetSource":
                source_type = "worksheet"
                ref = (child.attrib.get("ref") or "").strip()
                sheet = (child.attrib.get("sheet") or "").strip()
                name_attr = (child.attrib.get("name") or "").strip()
                source_sheet = sheet
                source_ref_range = ref
                if name_attr:
                    source_name = name_attr
                    source_type = "table"
                    source_ref = f"{sheet}!{name_attr}" if sheet else name_attr
                elif sheet and ref:
                    source_ref = f"{sheet}!{ref}"
                elif ref:
                    source_ref = ref
                elif sheet:
                    source_ref = f"{sheet} (entire sheet)"
                else:
                    source_ref = "Unknown range"
                break

            if ln == "consolidation":
                source_type = "consolidation"
                source_ref = "Multiple ranges"
                break

        if source_type == "unknown" and conn_id:
            source_type = "connection"
            source_ref = f"Connection ID: {conn_id}"

        break

    field_idx_sources: dict[str, str] = {}
    if source_type in {"worksheet", "table"}:
        columns = _columns_from_ref(source_ref_range)
        for idx, field in enumerate(field_names):
            idx_key = str(idx)
            col = columns[idx] if idx < len(columns) else ""
            if source_type == "table" and source_name:
                table_ref = f"{source_name}[{field}]" if field else source_name
                if source_sheet:
                    table_ref = f"{source_sheet}!{table_ref}"
                field_idx_sources[idx_key] = table_ref
            elif source_sheet and col:
                field_idx_sources[idx_key] = f"{source_sheet}!{col}"
            elif col:
                field_idx_sources[idx_key] = col
            elif source_ref:
                field_idx_sources[idx_key] = source_ref

    return (
        source_type,
        source_ref,
        field_names,
        field_idx_map,
        field_idx_sources,
        source_name,
    )


@dataclass(slots=True)
class PivotZipBackend:
    """Extract pivot tables and pivot caches from OOXML parts.

    This is best-effort and focuses on:
    - pivot table name
    - sheet placement (via worksheet relationships)
    - cacheId
    - cache source (worksheet vs connection) when available
    - measures (dataFields) and basic row/column grouping field names
    """

    name: str = "pivot_zip"

    def can_handle(self, ctx: AnalysisContext) -> bool:
        """Return True when pivot extraction is enabled and supported."""
        p = ctx.path
        if not ctx.options.include_pivots:
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
        """Extract pivot caches and pivot tables from OOXML parts."""
        report = BackendReport(backend=self.name)
        p: Path = ctx.path
        zip_ctx = zip_ctx or OOXMLZipContext.from_path(p)

        pivots = 0
        caches = 0

        try:
            with zipfile.ZipFile(p) as zf:
                if not _is_ooxml_excel_names(zip_ctx.names_set(zf)):
                    report.add_issue("not an OOXML Excel workbook", kind="unsupported")
                    report.stats = graph.stats()
                    return report

                sheet_path_to_name = _get_sheet_path_to_name(zf, zip_ctx)
                pt_to_sheet = _get_pivot_table_to_sheet(zf, zip_ctx, sheet_path_to_name)

                cache_id_to_rid = _get_cache_id_to_rid(zf, zip_ctx)
                rid_to_cache = _get_rid_to_cache_def_path(zf, zip_ctx)

                cache_info_by_id: dict[str, dict[str, Any]] = {}
                field_idx_by_cache_id: dict[str, dict[str, str]] = {}
                name_to_defined_ids: dict[str, list[str]] = {}

                for n in graph.nodes.values():
                    if n.kind != "defined_name":
                        continue
                    nm = str(n.attrs.get("name") or "").strip()
                    if nm:
                        name_to_defined_ids.setdefault(nm.lower(), []).append(n.id)

                # Connection nodes allow linking pivot caches to external data.
                conn_id_to_node_id: dict[str, str] = {}
                for n in graph.nodes.values():
                    if n.kind != "connection":
                        continue
                    cid = str(n.attrs.get("connection_id") or "").strip()
                    if cid:
                        conn_id_to_node_id[cid] = n.id

                for cache_id, rid in cache_id_to_rid.items():
                    cache_path = rid_to_cache.get(rid)
                    if not cache_path:
                        continue
                    (
                        source_type,
                        source_ref,
                        field_names,
                        field_idx_map,
                        field_idx_sources,
                        source_name,
                    ) = _parse_cache_definition(zf, zip_ctx, cache_path)

                    key = f"{cache_id}|{source_type}|{source_ref}"
                    cache_node = graph.upsert(
                        PivotCache.make(
                            key=key,
                            id=f"pcache:{key}",
                            cache_id=cache_id,
                            source_type=source_type,  # type: ignore[arg-type]
                            source_ref=source_ref,
                            extra={
                                "ooxml_part": cache_path,
                                "fields": field_names,
                                "field_index_sources": field_idx_sources,
                            },
                        )
                    )
                    cache_info_by_id[cache_id] = {
                        "node": cache_node,
                        "source_type": source_type,
                        "source_ref": source_ref,
                    }
                    field_idx_by_cache_id[cache_id] = field_idx_map
                    caches += 1

                    if source_name:
                        for dn_id in name_to_defined_ids.get(source_name.lower(), []):
                            graph.add_edge(cache_node.id, dn_id, "uses_defined_name")

                    # Optional link to a connection node if we can match by connection_id.
                    if source_type == "connection":
                        m = re.search(r"Connection ID:\s*(\d+)", source_ref)
                        if m:
                            conn_id = m.group(1)
                            node_id = conn_id_to_node_id.get(conn_id)
                            if node_id:
                                graph.add_edge(
                                    cache_node.id, node_id, "uses_connection"
                                )

                seen: set[tuple[str, str, str]] = set()
                for pt_path in zip_ctx.namelist(zf):
                    if not pt_path.startswith(
                        "xl/pivotTables/pivotTable"
                    ) or not pt_path.endswith(".xml"):
                        continue

                    data = zip_ctx.read_member(pt_path, zf=zf)
                    if not data:
                        continue

                    try:
                        root = ET.fromstring(data)
                    except ET.ParseError:
                        continue

                    pt_name = (
                        root.attrib.get("name") or "PivotTable"
                    ).strip() or "PivotTable"
                    cache_id = (root.attrib.get("cacheId") or "").strip()
                    sheet_name = pt_to_sheet.get(pt_path, "Unknown")

                    uniq = (pt_name, sheet_name, cache_id)
                    if uniq in seen:
                        continue
                    seen.add(uniq)

                    measures: list[dict[str, Any]] = []
                    grouping_fields: list[dict[str, Any]] = []

                    for el in root.iter():
                        if _localname(el.tag) == "dataField":
                            nm = (el.attrib.get("name") or "").strip()
                            subtotal = (el.attrib.get("subtotal") or "sum").strip()
                            if nm:
                                measures.append({"name": nm, "aggregation": subtotal})

                    for el in root.iter():
                        ln = _localname(el.tag)
                        if ln == "rowFields":
                            for f in el:
                                if _localname(f.tag) == "field":
                                    grouping_fields.append(
                                        {
                                            "field_index": f.attrib.get("x", ""),
                                            "axis": "row",
                                        }
                                    )
                        if ln == "colFields":
                            for f in el:
                                if _localname(f.tag) == "field":
                                    grouping_fields.append(
                                        {
                                            "field_index": f.attrib.get("x", ""),
                                            "axis": "column",
                                        }
                                    )

                    field_names = field_idx_by_cache_id.get(cache_id, {})
                    for gf in grouping_fields:
                        idx = str(gf.get("field_index") or "")
                        gf["name"] = field_names.get(
                            idx, f"Field_{idx}" if idx else "Field"
                        )

                    sheet_key = _sheet_key(sheet_name)
                    key = f"{sheet_key}|{pt_name}|{cache_id}"
                    pt_node = graph.upsert(
                        PivotTable.make(
                            key=key,
                            id=f"pivot:{key}",
                            name=pt_name,
                            sheet_name=sheet_name,
                            measures=measures,
                            grouping_fields=[
                                {"name": gf.get("name", ""), "axis": gf.get("axis", "")}
                                for gf in grouping_fields
                            ],
                            extra={"ooxml_part": pt_path, "cache_id": cache_id},
                        )
                    )
                    pivots += 1

                    sheet = graph.get_by_key("sheet", sheet_key)
                    if sheet:
                        graph.add_edge(sheet.id, pt_node.id, "contains")

                    cache_node = cache_info_by_id.get(cache_id, {}).get("node")
                    if cache_node:
                        graph.add_edge(pt_node.id, cache_node.id, "uses_cache")

        except Exception as e:  # noqa: BLE001
            report.add_issue(str(e), kind="runtime")

        report.stats = {"pivot_tables": pivots, "pivot_caches": caches, **graph.stats()}
        return report
