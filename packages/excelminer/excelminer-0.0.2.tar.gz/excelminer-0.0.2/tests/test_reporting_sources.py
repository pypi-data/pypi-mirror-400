from __future__ import annotations

from excelminer.model.entities import Source
from excelminer.model.graph import WorkbookGraph
from excelminer.reporting import list_sources, summarize_sources


def test_list_sources_stable_and_complete() -> None:
    g = WorkbookGraph()

    s1 = g.upsert(
        Source.make(
            source_type="sqlserver",
            key="sqlserver|HOST|DB",
            id="src:sqlserver|HOST|DB",
            server="HOST",
            database="DB",
            provider="SQLOLEDB",
        )
    )
    s2 = g.upsert(
        Source.make(
            source_type="file",
            key="file|C:/data/local.csv",
            id="src:file|C:/data/local.csv",
            value="C:/data/local.csv",
            provider="textPr",
        )
    )

    rows = list_sources(g)
    assert [r["id"] for r in rows] == sorted([s1.id, s2.id], key=str)

    # Ensure expected keys exist
    for r in rows:
        assert set(r.keys()) == {
            "id",
            "key",
            "source_type",
            "server",
            "database",
            "value",
            "provider",
        }


def test_summarize_sources_counts() -> None:
    g = WorkbookGraph()
    g.upsert(
        Source.make(
            source_type="web",
            key="web|https://example.com/data.csv",
            id="src:web|https://example.com/data.csv",
            value="https://example.com/data.csv",
            provider="webPr",
        )
    )
    g.upsert(
        Source.make(
            source_type="web",
            key="web|https://example.com/data2.csv",
            id="src:web|https://example.com/data2.csv",
            value="https://example.com/data2.csv",
            provider="webPr",
        )
    )
    g.upsert(
        Source.make(
            source_type="odbc_dsn",
            key="odbc_dsn|MyDsn",
            id="src:odbc_dsn|MyDsn",
            value="MyDsn",
            provider="odbc",
        )
    )

    summary = summarize_sources(g)
    assert summary["counts"]["total"] == 3
    assert summary["counts"]["by_type"] == {"odbc_dsn": 1, "web": 2}
    assert summary["counts"]["by_provider"] == {"odbc": 1, "webPr": 2}
