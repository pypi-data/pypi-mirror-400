from __future__ import annotations

import tracemalloc
from pathlib import Path
from typing import Iterable

import pytest

from excelminer.backends.base import AnalysisContext, AnalysisOptions, BackendReport
from excelminer.backends.com_backend import ComBackend
from excelminer.backends.ooxml_zip import OOXMLZipBackend
from excelminer.backends.openpyxl_backend import _extract_deps  # type: ignore
from excelminer.model.entities import Connection, Edge, Sheet, Source
from excelminer.model.graph import WorkbookGraph
from excelminer.model.normalize import normalize_connection_key, normalize_source_key
from excelminer.rationalization.formulas import abstract_formulas
from tests.fixtures.workbooks import write_partial_ooxml_zip


def test_entities_to_dict_and_factories() -> None:
    e = Edge(src="a", dst="b", kind="k", attrs={"x": 1})
    assert e.to_dict()["attrs"]["x"] == 1

    c = Connection.make(key="k", id="conn:k", name="n", raw="abc", details={"d": 1})
    d = c.to_dict()
    assert d["kind"] == "connection"
    assert d["attrs"]["name"] == "n"
    assert d["attrs"]["raw"] == "abc"
    assert d["attrs"]["d"] == 1

    s = Source.make(
        source_type="sqlserver", key="k", id="src:k", server="h", database="db"
    )
    sd = s.to_dict()
    assert sd["kind"] == "source"
    assert sd["attrs"]["server"] == "h"
    assert sd["attrs"]["database"] == "db"


def test_graph_get_or_create_calls_factory_once() -> None:
    g = WorkbookGraph()
    calls: list[str] = []

    def factory() -> Sheet:
        calls.append("x")
        return Sheet.make(key="A", id="sheet:A", name="A")

    a1 = g.get_or_create("sheet", "A", factory)
    a2 = g.get_or_create("sheet", "A", factory)
    assert a1 is a2
    assert calls == ["x"]


@pytest.mark.parametrize(
    "formula,expected",
    [
        ("=SUM(A1:A2)", {"refs": [{"kind": "range", "sheet": "", "range": "A1:A2"}]}),
        (
            "='My Sheet'!$B$2 + Sheet2!C3",
            {
                "refs": [
                    {"sheet": "My Sheet", "cell": "B2"},
                    {"sheet": "Sheet2", "cell": "C3"},
                ]
            },
        ),
        (
            "=SUM(Table1[Amount])",
            {"refs": [{"kind": "structured", "structured": "Table1[Amount]"}]},
        ),
        (
            "='[Budget.xlsx]Summary'!$A$1 + [Other.xlsx]Sheet1!B2",
            {
                "refs": [
                    {
                        "kind": "external",
                        "workbook": "Budget.xlsx",
                        "sheet": "Summary",
                        "cell": "A1",
                    },
                    {
                        "kind": "external",
                        "workbook": "Other.xlsx",
                        "sheet": "Sheet1",
                        "cell": "B2",
                    },
                ]
            },
        ),
        (
            "=SUM(Sheet1!A1:B2)",
            {"refs": [{"kind": "range", "sheet": "Sheet1", "range": "A1:B2"}]},
        ),
        (
            "=MyNamedValue+1",
            {"refs": [{"kind": "name", "name": "MyNamedValue"}]},
        ),
        ("=1+2", {}),
        ("", {}),
    ],
)
def test_extract_deps_edge_cases(formula: str, expected: dict[str, object]) -> None:
    assert _extract_deps(formula) == expected


def test_ooxml_zip_backend_web_and_text_connections(tmp_path: Path) -> None:
    content_types = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\"></Types>
"""
    workbook_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">
  <sheets>
    <sheet name=\"S\" sheetId=\"1\"/>
  </sheets>
</workbook>
"""
    connections_xml = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<connections xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">
  <connection id=\"1\" name=\"WebConn\">
    <webPr url=\"https://example.com\" />
  </connection>
  <connection id=\"2\" name=\"TextConn\">
    <textPr sourceFile=\"C:\\data.csv\" />
  </connection>
</connections>
"""

    xlsx = tmp_path / "conn_types.xlsx"
    write_partial_ooxml_zip(
        xlsx,
        {
            "[Content_Types].xml": content_types,
            "xl/workbook.xml": workbook_xml,
            "xl/connections.xml": connections_xml,
        },
    )

    ctx = AnalysisContext(
        path=xlsx,
        options=AnalysisOptions(include_connections=True, include_defined_names=False),
    )
    g = WorkbookGraph()
    rep = OOXMLZipBackend().extract(ctx, g)
    assert rep.issues == []

    conns = [n for n in g.nodes.values() if n.kind == "connection"]
    assert len(conns) == 2
    kinds = {c.attrs.get("connection_kind") for c in conns}
    assert "web" in kinds
    assert "text" in kinds


def test_ooxml_zip_backend_handles_malformed_xml(tmp_path: Path) -> None:
    # workbook.xml is malformed; backend should not crash.
    content_types = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\"></Types>
"""
    xlsx = tmp_path / "bad.xlsx"
    write_partial_ooxml_zip(
        xlsx,
        {
            "[Content_Types].xml": content_types,
            "xl/workbook.xml": "<workbook><notclosed>",
        },
    )

    ctx = AnalysisContext(
        path=xlsx,
        options=AnalysisOptions(include_connections=False, include_defined_names=True),
    )
    g = WorkbookGraph()
    rep = OOXMLZipBackend().extract(ctx, g)
    # No exception; report exists.
    assert rep.backend == "ooxml_zip"
    assert rep.stats["nodes"] == len(g.nodes)


def test_com_backend_extract_reports_missing_pywin32(tmp_path: Path) -> None:
    p = tmp_path / "x.xlsx"
    p.write_bytes(b"dummy")
    ctx = AnalysisContext(path=p)

    b = ComBackend()
    if not b.can_handle(ctx):
        pytest.skip("COM backend not applicable on this platform")

    rep = b.extract(ctx, WorkbookGraph())
    assert rep.backend == "com"
    assert rep.stats
    # In most envs, pywin32 won't be installed; either way, we shouldn't crash.
    assert isinstance(rep.issues, list)


def test_streaming_backend_memory_stays_bounded(tmp_path: Path) -> None:
    class StreamingBackend:
        name = "streaming"

        def can_handle(self, ctx: AnalysisContext) -> bool:
            return True

        def extract(self, ctx: AnalysisContext, graph: WorkbookGraph) -> BackendReport:
            report = BackendReport(backend=self.name)

            def node_iter() -> Iterable[Sheet]:
                for i in range(10_000):
                    key = f"S{i}"
                    yield Sheet.make(key=key, id=f"sheet:{key}", name=key)

            def edge_iter() -> Iterable[Edge]:
                for i in range(9_999):
                    src = f"sheet:S{i}"
                    dst = f"sheet:S{i + 1}"
                    yield Edge(src=src, dst=dst, kind="next")

            graph.add_nodes(node_iter())
            graph.add_edges(edge_iter())
            report.stats = graph.stats()
            return report

    wb = tmp_path / "large.xlsx"
    wb.write_bytes(b"dummy")

    tracemalloc.start()
    _graph = WorkbookGraph()
    StreamingBackend().extract(AnalysisContext(path=wb), _graph)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    overhead = peak - current
    assert overhead < 10 * 1024 * 1024


def test_abstract_formulas_include_dependency_hints() -> None:
    entries = [
        {
            "sheet": "Data",
            "address": "A1",
            "formula": "=B1+C1",
            "deps": {
                "refs": [
                    {"sheet": "", "cell": "B1"},
                    {"sheet": "", "cell": "C1"},
                ]
            },
        },
        {
            "sheet": "Data",
            "address": "A2",
            "formula": "=B2+C2",
            "deps": {
                "refs": [
                    {"sheet": "", "cell": "B2"},
                    {"sheet": "", "cell": "C2"},
                ]
            },
        },
    ]

    groups = abstract_formulas(entries, include_ref_hints=True)
    assert len(groups) == 1

    group = groups[0]
    assert group["count"] == 2
    assert group["address_ranges"] == ["A1:A2"]
    assert group["ref_hints"]["ref1"]["kind"] == "relative"
    assert group["ref_hints"]["ref1"]["offset"] == {"dr": 0, "dc": 1}
    assert group["ref_hints"]["ref2"]["kind"] == "relative"
    assert group["ref_hints"]["ref2"]["offset"] == {"dr": 0, "dc": 2}


def test_overlapping_backend_discoveries_dedupe_connections_and_sources() -> None:
    graph = WorkbookGraph()

    conn_key_a = normalize_connection_key("Sales | 1")
    graph.upsert(
        Connection.make(
            key=conn_key_a,
            id="conn:1",
            name="Sales",
            raw="a",
            details={"x": 1},
        )
    )

    conn_key_b = normalize_connection_key("sales|1")
    graph.upsert(
        Connection.make(
            key=conn_key_b,
            id="conn:2",
            name="Sales",
            raw="b",
            details={"x": 2},
        )
    )

    source_key_a = normalize_source_key("file|C:\\Data\\Report.csv")
    graph.upsert(
        Source.make(
            source_type="file",
            key=source_key_a,
            id="src:1",
            value="C:\\Data\\Report.csv",
        )
    )

    source_key_b = normalize_source_key("file|file:///C:/Data/Report.csv")
    graph.upsert(
        Source.make(
            source_type="file",
            key=source_key_b,
            id="src:2",
            value="file:///C:/Data/Report.csv",
        )
    )

    conns = [n for n in graph.nodes.values() if n.kind == "connection"]
    sources = [n for n in graph.nodes.values() if n.kind == "source"]

    assert len(conns) == 1
    assert conns[0].id == "conn:1"
    assert len(sources) == 1
    assert sources[0].id == "src:1"
