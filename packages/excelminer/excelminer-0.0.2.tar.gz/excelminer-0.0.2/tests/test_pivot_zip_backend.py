from __future__ import annotations

import zipfile
from pathlib import Path

from excelminer.backends.base import AnalysisContext, AnalysisOptions
from excelminer.backends.ooxml_zip import OOXMLZipBackend
from excelminer.backends.pivot_zip import PivotZipBackend
from excelminer.model.graph import WorkbookGraph


def test_pivot_zip_backend_extracts_pivots_and_caches_and_links_connection(
    tmp_path: Path,
) -> None:
    xlsx = tmp_path / "pivot.xlsx"

    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
</Types>
"""

    workbook_xml = """<?xml version="1.0" encoding="UTF-8"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
          xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="Sheet1" sheetId="1" r:id="rId1" />
  </sheets>
  <pivotCaches>
    <pivotCache cacheId="1" r:id="rId2" />
  </pivotCaches>
</workbook>
"""

    workbook_rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/pivotCacheDefinition" Target="pivotCache/pivotCacheDefinition1.xml"/>
</Relationships>
"""

    sheet1_xml = """<?xml version="1.0" encoding="UTF-8"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" />
"""

    sheet1_rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId9" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/pivotTable" Target="../pivotTables/pivotTable1.xml"/>
</Relationships>
"""

    pivot_cache_def = """<?xml version="1.0" encoding="UTF-8"?>
<pivotCacheDefinition xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <cacheSource connectionId="1" />
  <cacheFields count="2">
    <cacheField name="Region" />
    <cacheField name="Amount" />
  </cacheFields>
</pivotCacheDefinition>
"""

    pivot_table_xml = """<?xml version="1.0" encoding="UTF-8"?>
<pivotTableDefinition xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" name="Pivot1" cacheId="1">
  <pivotFields count="2" />
  <rowFields count="1">
    <field x="0" />
  </rowFields>
  <dataFields count="1">
    <dataField name="Sum of Amount" subtotal="sum" />
  </dataFields>
</pivotTableDefinition>
"""

    connections_xml = """<?xml version="1.0" encoding="UTF-8"?>
<connections xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <connection id="1" name="Conn1" type="1">
    <dbPr connection="Provider=SQLOLEDB;Server=host;Database=db;User Id=foo;Password=bar;" />
  </connection>
</connections>
"""

    with zipfile.ZipFile(xlsx, "w") as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("xl/workbook.xml", workbook_xml)
        zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        zf.writestr("xl/worksheets/sheet1.xml", sheet1_xml)
        zf.writestr("xl/worksheets/_rels/sheet1.xml.rels", sheet1_rels)
        zf.writestr("xl/pivotCache/pivotCacheDefinition1.xml", pivot_cache_def)
        zf.writestr("xl/pivotTables/pivotTable1.xml", pivot_table_xml)
        zf.writestr("xl/connections.xml", connections_xml)

    g = WorkbookGraph()
    ctx = AnalysisContext(
        path=xlsx,
        options=AnalysisOptions(include_pivots=True, include_connections=True),
    )

    # Seed sheets + connections.
    OOXMLZipBackend().extract(ctx, g)
    PivotZipBackend().extract(ctx, g)

    pivot_nodes = [n for n in g.nodes.values() if n.kind == "pivot_table"]
    assert len(pivot_nodes) == 1
    assert pivot_nodes[0].attrs.get("name") == "Pivot1"
    assert pivot_nodes[0].attrs.get("sheet") == "Sheet1"

    cache_nodes = [n for n in g.nodes.values() if n.kind == "pivot_cache"]
    assert len(cache_nodes) == 1
    assert cache_nodes[0].attrs.get("cache_id") == "1"

    # pivot_table -> pivot_cache
    assert any(e.kind == "uses_cache" for e in g.edges)

    # pivot_cache -> connection (by connection_id)
    assert any(e.kind == "uses_connection" for e in g.edges)
