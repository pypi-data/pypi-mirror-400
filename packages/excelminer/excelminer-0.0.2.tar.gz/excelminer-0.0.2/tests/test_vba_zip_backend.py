from __future__ import annotations

import zipfile
from pathlib import Path

from excelminer.backends.base import AnalysisContext, AnalysisOptions
from excelminer.backends.vba_zip import VbaZipBackend
from excelminer.model.graph import WorkbookGraph


def test_vba_zip_backend_detects_vba_project_bin(tmp_path: Path) -> None:
    xlsm = tmp_path / "macros.xlsm"

    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
</Types>
"""

    workbook_xml = """<?xml version="1.0" encoding="UTF-8"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"/>
"""

    with zipfile.ZipFile(xlsm, "w") as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("xl/workbook.xml", workbook_xml)
        zf.writestr("xl/vbaProject.bin", b"\x01\x02\x03\x04")

    g = WorkbookGraph()
    ctx = AnalysisContext(path=xlsm, options=AnalysisOptions(include_vba=True))
    rep = VbaZipBackend().extract(ctx, g)

    assert rep.issues == []
    assert rep.stats is not None
    assert rep.stats.get("vba_projects") == 1

    vba_nodes = [n for n in g.nodes.values() if n.kind == "vba_project"]
    assert len(vba_nodes) == 1
    assert vba_nodes[0].attrs.get("has_vba") is True
    parts = vba_nodes[0].attrs.get("parts")
    assert isinstance(parts, list)
    assert any(p.get("part") == "xl/vbaProject.bin" for p in parts)


def test_vba_zip_backend_respects_include_vba_flag(tmp_path: Path) -> None:
    xlsm = tmp_path / "macros.xlsm"
    with zipfile.ZipFile(xlsm, "w") as zf:
        zf.writestr(
            "[Content_Types].xml",
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>',
        )
        zf.writestr(
            "xl/workbook.xml",
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"/>',
        )
        zf.writestr("xl/vbaProject.bin", b"\x00")

    assert (
        VbaZipBackend().can_handle(
            AnalysisContext(path=xlsm, options=AnalysisOptions(include_vba=False))
        )
        is False
    )
