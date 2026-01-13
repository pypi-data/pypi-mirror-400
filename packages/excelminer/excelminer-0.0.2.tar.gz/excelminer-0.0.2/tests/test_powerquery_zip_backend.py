from __future__ import annotations

import zipfile
from pathlib import Path

from excelminer.backends.base import AnalysisContext, AnalysisOptions
from excelminer.backends.ooxml_zip import OOXMLZipBackend
from excelminer.backends.powerquery_zip import PowerQueryZipBackend
from excelminer.model.graph import WorkbookGraph


def test_powerquery_zip_backend_extracts_queries_and_sources(tmp_path: Path) -> None:
    xlsx = tmp_path / "pq.xlsx"

    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
</Types>
"""

    workbook_xml = """<?xml version="1.0" encoding="UTF-8"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"/>
"""

    query_xml = """<?xml version="1.0" encoding="UTF-8"?>
<query name="My Query">
  <script>let
    Source = Sql.Database("myserver", "mydb")
  in
    Source</script>
</query>
"""

    with zipfile.ZipFile(xlsx, "w") as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("xl/workbook.xml", workbook_xml)
        zf.writestr("xl/queries/query1.xml", query_xml)

    g = WorkbookGraph()
    ctx = AnalysisContext(path=xlsx, options=AnalysisOptions(include_powerquery=True))

    rep = PowerQueryZipBackend().extract(ctx, g)
    assert rep.backend == "powerquery_zip"

    pq_nodes = [n for n in g.nodes.values() if n.kind == "powerquery"]
    assert len(pq_nodes) == 1
    assert pq_nodes[0].attrs.get("name") == "My Query"
    assert pq_nodes[0].attrs.get("script_count") == 1

    script_nodes = [n for n in g.nodes.values() if n.kind == "m_script"]
    assert len(script_nodes) == 1
    assert "Sql.Database" in (script_nodes[0].attrs.get("m_code") or "")

    assert any(e.kind == "has_script" for e in g.edges)

    src_nodes = [n for n in g.nodes.values() if n.kind == "source"]
    assert any(s.attrs.get("source_type") == "sqlserver" for s in src_nodes)

    # powerquery -> source edge
    assert any(e.kind == "uses_source" for e in g.edges)


def test_powerquery_zip_backend_extracts_m_scripts_from_mashup_bin(
    tmp_path: Path,
) -> None:
    xlsx = tmp_path / "mashup_scripts.xlsx"

    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
</Types>
"""

    workbook_xml = """<?xml version="1.0" encoding="UTF-8"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"/>
"""

    mashup_script = (
        'section TestSection;\nlet\n  Source = Sql.Database("mashup", "db")\n'
        "in\n  Source\n"
    )

    with zipfile.ZipFile(xlsx, "w") as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("xl/workbook.xml", workbook_xml)
        zf.writestr("xl/mashup/mashup.bin", mashup_script.encode("utf-8"))

    g = WorkbookGraph()
    ctx = AnalysisContext(path=xlsx, options=AnalysisOptions(include_powerquery=True))

    rep = PowerQueryZipBackend().extract(ctx, g)

    assert rep.stats is not None
    assert rep.stats.get("power_query_mashup_containers") == 1
    assert rep.stats.get("power_query_mashup_scripts") == 1

    script_nodes = [n for n in g.nodes.values() if n.kind == "m_script"]
    assert len(script_nodes) == 1
    assert script_nodes[0].attrs.get("name") == "TestSection"
    assert "Sql.Database" in (script_nodes[0].attrs.get("m_code") or "")

    assert any(e.kind == "has_script" for e in g.edges)


def test_powerquery_zip_backend_detects_mashup_container_without_queries_xml(
    tmp_path: Path,
) -> None:
    xlsx = tmp_path / "mashup_only.xlsx"

    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
</Types>
"""

    workbook_xml = """<?xml version="1.0" encoding="UTF-8"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"/>
"""

    # A Mashup connection can exist even when `xl/queries/*.xml` is absent.
    connections_xml = """<?xml version="1.0" encoding="UTF-8"?>
<connections xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <connection id="1" name="MashupConn" type="1">
    <dbPr connection="Provider=Microsoft.Mashup.OleDb.1;Data Source=$Workbook$" />
  </connection>
</connections>
"""

    with zipfile.ZipFile(xlsx, "w") as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("xl/workbook.xml", workbook_xml)
        zf.writestr("xl/connections.xml", connections_xml)
        zf.writestr("xl/mashup/mashup.bin", b"\x00\x01\x02")

    g = WorkbookGraph()
    ctx = AnalysisContext(
        path=xlsx,
        options=AnalysisOptions(include_connections=True, include_powerquery=True),
    )

    # Ensure connection nodes exist for `uses_connection` linking.
    OOXMLZipBackend().extract(ctx, g)
    rep = PowerQueryZipBackend().extract(ctx, g)

    assert rep.stats is not None
    assert rep.stats.get("power_query_mashup_containers") == 1

    pq_nodes = [n for n in g.nodes.values() if n.kind == "powerquery"]
    assert len(pq_nodes) == 1
    assert pq_nodes[0].attrs.get("mashup_container") is True
    assert pq_nodes[0].attrs.get("mashup_connection_ids") == ["1"]

    mashup_parts = pq_nodes[0].attrs.get("mashup_parts")
    assert isinstance(mashup_parts, list)
    assert any(p.get("part") == "xl/mashup/mashup.bin" for p in mashup_parts)

    # powerquery -> connection edge
    assert any(e.kind == "uses_connection" for e in g.edges)
