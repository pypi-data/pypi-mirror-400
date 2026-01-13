from __future__ import annotations

from excelminer.model.entities import Connection, Source
from excelminer.model.graph import WorkbookGraph
from excelminer.reporting import summarize_connections


def test_summarize_connections_includes_uses_source_edges() -> None:
    g = WorkbookGraph()

    conn = g.upsert(
        Connection.make(
            key="MyConn|1",
            id="conn:MyConn|1",
            name="MyConn",
            connection_kind="oledb",
            raw=None,
            details={"connection_id": "1"},
        )
    )
    src = g.upsert(
        Source.make(
            source_type="sqlserver",
            key="sqlserver|HOST|DB",
            id="src:sqlserver|HOST|DB",
            server="HOST",
            database="DB",
            provider="SQLOLEDB",
        )
    )
    g.add_edge(conn.id, src.id, "uses_source")

    summary = summarize_connections(g)
    assert summary["counts"]["total"] == 1
    assert summary["counts"]["connected_to_sources"] == 1
    assert summary["counts"]["by_kind"] == {"oledb": 1}

    uses = summary["uses_source"]
    assert uses[conn.id] == [src.id]
