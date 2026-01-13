from __future__ import annotations

import pytest

from excelminer.model.entities import Edge, Sheet
from excelminer.model.graph import WorkbookGraph


def test_graph_upsert_dedupes_by_kind_key() -> None:
    g = WorkbookGraph()

    s1 = Sheet.make(key="Sheet1", id="sheet:Sheet1", name="Sheet1")
    s2 = Sheet.make(key="Sheet1", id="sheet:DifferentId", name="Sheet1")

    a = g.upsert(s1)
    b = g.upsert(s2)

    assert a is b
    assert len(g.nodes) == 1
    assert g.get_by_key("sheet", "Sheet1") is a


def test_graph_add_edge_requires_nodes() -> None:
    g = WorkbookGraph()
    s1 = g.upsert(Sheet.make(key="A", id="sheet:A", name="A"))

    with pytest.raises(KeyError):
        g.add_edge(s1.id, "missing", "contains")

    with pytest.raises(KeyError):
        g.add_edge("missing", s1.id, "contains")


def test_graph_add_edge_happy_path_and_get() -> None:
    g = WorkbookGraph()
    a = g.upsert(Sheet.make(key="A", id="sheet:A", name="A"))
    b = g.upsert(Sheet.make(key="B", id="sheet:B", name="B"))

    e = g.add_edge(a.id, b.id, "rel", weight=1)
    assert e.kind == "rel"
    assert e.attrs["weight"] == 1
    assert g.get(a.id) is a
    assert g.get("missing") is None


def test_graph_add_edges_requires_nodes() -> None:
    g = WorkbookGraph()
    a = g.upsert(Sheet.make(key="A", id="sheet:A", name="A"))
    b = g.upsert(Sheet.make(key="B", id="sheet:B", name="B"))

    g.add_edges([Edge(src=a.id, dst=b.id, kind="rel")])
    assert len(g.edges) == 1

    with pytest.raises(KeyError):
        g.add_edges([Edge(src="missing", dst=b.id, kind="rel")])


def test_graph_to_dict_contains_stats() -> None:
    g = WorkbookGraph()
    g.upsert(Sheet.make(key="A", id="sheet:A", name="A"))
    d = g.to_dict()

    assert "nodes" in d and "edges" in d and "stats" in d
    assert d["stats"]["nodes"] == 1
    assert d["stats"]["edges"] == 0
    assert d["stats"]["nodes_sheet"] == 1
