from __future__ import annotations

import zipfile
from pathlib import Path

from excelminer.backends.base import AnalysisContext, AnalysisOptions
from excelminer.backends.ooxml_zip import OOXMLZipBackend, OOXMLZipContext
from excelminer.backends.pivot_zip import PivotZipBackend
from excelminer.backends.powerquery_zip import PowerQueryZipBackend
from excelminer.model.entities import Connection
from excelminer.model.graph import WorkbookGraph
from excelminer.model.normalize import normalize_connection_key


def _write_minimal_ooxml_zip(
    path: Path,
    *,
    workbook_xml: str,
    connections_xml: str | None = None,
    extra_parts: dict[str, str] | None = None,
) -> None:
    # Minimal structure to satisfy OOXMLZipBackend._is_ooxml_excel
    content_types = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\"></Types>
"""

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("xl/workbook.xml", workbook_xml)
        if connections_xml is not None:
            zf.writestr("xl/connections.xml", connections_xml)
        if extra_parts:
            for part_name, payload in extra_parts.items():
                zf.writestr(part_name, payload)


def test_ooxml_zip_backend_extracts_sheets_and_defined_names(tmp_path: Path) -> None:
    workbook_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">
  <sheets>
    <sheet name=\"Sheet One\" sheetId=\"1\"/>
    <sheet name=\"Second\" sheetId=\"2\"/>
  </sheets>
  <definedNames>
    <definedName name=\"MyName\">Sheet One!$A$1</definedName>
    <definedName name=\"LocalName\" localSheetId=\"0\">$B$2</definedName>
  </definedNames>
</workbook>
"""

    xlsx = tmp_path / "minimal.xlsx"
    _write_minimal_ooxml_zip(xlsx, workbook_xml=workbook_xml)

    ctx = AnalysisContext(
        path=xlsx,
        options=AnalysisOptions(include_connections=False, include_defined_names=True),
    )
    g = WorkbookGraph()
    report = OOXMLZipBackend().extract(ctx, g)

    assert report.backend == "ooxml_zip"
    assert report.issues == []

    kinds = {n.kind for n in g.nodes.values()}
    assert "sheet" in kinds
    assert "defined_name" in kinds

    # Both sheets should exist
    assert g.get_by_key("sheet", "Sheet One") is not None
    assert g.get_by_key("sheet", "Second") is not None


def test_ooxml_zip_backend_parses_connections_and_sanitizes(tmp_path: Path) -> None:
    workbook_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">
  <sheets>
    <sheet name=\"Sheet1\" sheetId=\"1\"/>
  </sheets>
</workbook>
"""

    connections_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<connections xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">
  <connection id=\"1\" name=\"MyConn\" type=\"1\">
    <dbPr connection=\"Provider=SQLOLEDB;Data Source=HOST;Initial Catalog=DB;User ID=sa;Password=secret\" />
  </connection>
</connections>
"""

    xlsx = tmp_path / "with_connections.xlsx"
    _write_minimal_ooxml_zip(
        xlsx, workbook_xml=workbook_xml, connections_xml=connections_xml
    )

    ctx = AnalysisContext(
        path=xlsx,
        options=AnalysisOptions(include_connections=True, include_defined_names=False),
    )
    g = WorkbookGraph()
    report = OOXMLZipBackend().extract(ctx, g)

    assert report.issues == []

    conn = next((n for n in g.nodes.values() if n.kind == "connection"), None)
    assert conn is not None

    # Ensure sanitized connection string data made it into attrs
    kv = conn.attrs.get("connection_kv")
    assert isinstance(kv, dict)
    assert kv.get("password") == "***"
    assert kv.get("user id") == "***"

    # A Source should be created and connected
    src = next((n for n in g.nodes.values() if n.kind == "source"), None)
    assert src is not None

    assert any(
        e.src == conn.id and e.dst == src.id and e.kind == "uses_source"
        for e in g.edges
    )


def test_ooxml_zip_backend_parses_extended_properties(tmp_path: Path) -> None:
    workbook_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">
  <sheets>
    <sheet name=\"Sheet1\" sheetId=\"1\"/>
  </sheets>
</workbook>
"""

    connections_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<connections xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">
  <connection id=\"1\" name=\"ExcelConn\" type=\"1\">
    <dbPr connection=\"Provider=Microsoft.ACE.OLEDB.12.0;Data Source=C:/data/report.xlsx;Extended Properties=&quot;Excel 12.0;HDR=YES;IMEX=1&quot;;\" />
  </connection>
</connections>
"""

    xlsx = tmp_path / "extended_properties.xlsx"
    _write_minimal_ooxml_zip(
        xlsx, workbook_xml=workbook_xml, connections_xml=connections_xml
    )

    ctx = AnalysisContext(
        path=xlsx,
        options=AnalysisOptions(include_connections=True, include_defined_names=False),
    )
    g = WorkbookGraph()
    report = OOXMLZipBackend().extract(ctx, g)

    assert report.issues == []

    conn = next((n for n in g.nodes.values() if n.kind == "connection"), None)
    assert conn is not None
    kv = conn.attrs.get("connection_kv")
    assert isinstance(kv, dict)
    assert kv.get("extended properties") == "Excel 12.0;HDR=YES;IMEX=1"


def test_ooxml_zip_backend_discovers_external_links(tmp_path: Path) -> None:
    workbook_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">
  <sheets>
    <sheet name=\"Sheet1\" sheetId=\"1\"/>
  </sheets>
</workbook>
"""

    external_link_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<externalLink xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"
  xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\">
  <externalBook r:id=\"rId1\"/>
</externalLink>
"""

    external_link_rels = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">
  <Relationship
    Id=\"rId1\"
    Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/externalLinkPath\"
    Target=\"file:///C:/data/other.xlsx\"
    TargetMode=\"External\"/>
</Relationships>
"""

    xlsx = tmp_path / "with_external_links.xlsx"
    _write_minimal_ooxml_zip(
        xlsx,
        workbook_xml=workbook_xml,
        connections_xml=None,
        extra_parts={
            "xl/externalLinks/externalLink1.xml": external_link_xml,
            "xl/externalLinks/_rels/externalLink1.xml.rels": external_link_rels,
        },
    )

    ctx = AnalysisContext(
        path=xlsx,
        options=AnalysisOptions(include_connections=True, include_defined_names=False),
    )
    g = WorkbookGraph()
    report = OOXMLZipBackend().extract(ctx, g)

    assert report.issues == []

    sources = [n for n in g.nodes.values() if n.kind == "source"]
    assert any(
        (n.attrs.get("provider") == "externalLink")
        and (n.attrs.get("value") == "file:///C:/data/other.xlsx")
        for n in sources
    )

    # Ensure there's at least one uses_source edge from a synthetic connection.
    assert any(e.kind == "uses_source" for e in g.edges)


def test_ooxml_zip_backend_links_web_and_text_sources(tmp_path: Path) -> None:
    workbook_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">
    <sheets>
        <sheet name=\"Sheet1\" sheetId=\"1\"/>
    </sheets>
</workbook>
"""

    connections_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<connections xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">
    <connection id=\"1\" name=\"WebConn\" type=\"4\">
        <webPr url=\"https://example.com/data.csv\"/>
    </connection>
    <connection id=\"2\" name=\"TextConn\" type=\"2\">
        <textPr sourceFile=\"C:/data/local.csv\"/>
    </connection>
</connections>
"""

    xlsx = tmp_path / "web_and_text_sources.xlsx"
    _write_minimal_ooxml_zip(
        xlsx,
        workbook_xml=workbook_xml,
        connections_xml=connections_xml,
    )

    ctx = AnalysisContext(
        path=xlsx,
        options=AnalysisOptions(include_connections=True, include_defined_names=False),
    )
    g = WorkbookGraph()
    report = OOXMLZipBackend().extract(ctx, g)

    assert report.issues == []

    sources = [n for n in g.nodes.values() if n.kind == "source"]
    assert any(
        n.attrs.get("source_type") == "web"
        and n.attrs.get("value") == "https://example.com/data.csv"
        for n in sources
    )
    assert any(
        n.attrs.get("source_type") == "file"
        and n.attrs.get("value") == "C:/data/local.csv"
        for n in sources
    )

    # Confirm at least two uses_source edges (one for each connection).
    uses_source_edges = [e for e in g.edges if e.kind == "uses_source"]
    assert len(uses_source_edges) >= 2


def test_ooxml_zip_backend_can_handle_rejects_non_zip(tmp_path: Path) -> None:
    p = tmp_path / "not_a_zip.xlsx"
    p.write_text("nope", encoding="utf-8")

    ctx = AnalysisContext(path=p)
    assert OOXMLZipBackend().can_handle(ctx) is False


def test_ooxml_zip_context_caches_workbook_reads(tmp_path: Path, monkeypatch) -> None:
    workbook_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"
  xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\">
  <sheets>
    <sheet name=\"Sheet1\" sheetId=\"1\" r:id=\"rId1\"/>
  </sheets>
  <pivotCaches>
    <pivotCache cacheId=\"1\" r:id=\"rId2\"/>
  </pivotCaches>
</workbook>
"""

    workbook_rels = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">
  <Relationship
    Id=\"rId1\"
    Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\"
    Target=\"worksheets/sheet1.xml\"/>
  <Relationship
    Id=\"rId2\"
    Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/pivotCacheDefinition\"
    Target=\"pivotCache/pivotCacheDefinition1.xml\"/>
</Relationships>
"""

    xlsx = tmp_path / "cached_reads.xlsx"
    _write_minimal_ooxml_zip(
        xlsx,
        workbook_xml=workbook_xml,
        extra_parts={
            "xl/_rels/workbook.xml.rels": workbook_rels,
        },
    )

    open_counts: dict[str, int] = {"workbook": 0}
    original_open = zipfile.ZipFile.open

    def counting_open(self, name, *args, **kwargs):
        if name == "xl/workbook.xml":
            open_counts["workbook"] += 1
        return original_open(self, name, *args, **kwargs)

    monkeypatch.setattr(zipfile.ZipFile, "open", counting_open)

    ctx = AnalysisContext(
        path=xlsx,
        options=AnalysisOptions(
            include_connections=False,
            include_defined_names=False,
            include_pivots=True,
        ),
    )
    g = WorkbookGraph()
    zip_ctx = OOXMLZipContext.from_path(xlsx)

    OOXMLZipBackend().extract(ctx, g, zip_ctx=zip_ctx)
    PivotZipBackend().extract(ctx, g, zip_ctx=zip_ctx)

    assert open_counts["workbook"] <= 1


def test_ooxml_zip_backend_dedupes_sources_across_backends(
    tmp_path: Path,
) -> None:
    workbook_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">
  <sheets>
    <sheet name=\"Sheet1\" sheetId=\"1\"/>
  </sheets>
</workbook>
"""

    connections_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<connections xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">
  <connection id=\"1\" name=\"Sales Conn\" type=\"1\">
    <dbPr connection=\"Provider=SQLOLEDB;Data Source=HOST;Initial Catalog=SalesDb\" />
  </connection>
</connections>
"""

    query_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<query name=\"Sales Query\">
  <script>let
    Source = Sql.Database(\"host\", \"salesdb\")
  in
    Source</script>
</query>
"""

    xlsx = tmp_path / "dedupe_sources.xlsx"
    _write_minimal_ooxml_zip(
        xlsx,
        workbook_xml=workbook_xml,
        connections_xml=connections_xml,
        extra_parts={"xl/queries/query1.xml": query_xml},
    )

    ctx = AnalysisContext(
        path=xlsx,
        options=AnalysisOptions(include_connections=True, include_powerquery=True),
    )
    g = WorkbookGraph()

    OOXMLZipBackend().extract(ctx, g)
    PowerQueryZipBackend().extract(ctx, g)

    sql_sources = [
        n
        for n in g.nodes.values()
        if n.kind == "source" and n.attrs.get("source_type") == "sqlserver"
    ]
    assert len(sql_sources) == 1

    alt_key = normalize_connection_key("  SALES  CONN | 1 ")
    graph_before = len([n for n in g.nodes.values() if n.kind == "connection"])
    g.upsert(
        Connection.make(
            key=alt_key,
            id=f"conn:{alt_key}",
            name="SALES  CONN",
            connection_kind="oledb",
        )
    )
    graph_after = len([n for n in g.nodes.values() if n.kind == "connection"])
    assert graph_before == graph_after == 1
