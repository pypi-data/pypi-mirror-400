from __future__ import annotations

"""Summary/reporting helpers built on WorkbookGraph."""

from collections import Counter
from typing import Any

from excelminer.model.graph import WorkbookGraph


def list_sources(graph: WorkbookGraph) -> list[dict[str, Any]]:
    """Return a stable, JSON-friendly list of discovered data sources."""

    out: list[dict[str, Any]] = []
    for node in graph.nodes.values():
        if node.kind != "source":
            continue
        attrs = dict(node.attrs)
        out.append(
            {
                "id": node.id,
                "key": node.key,
                "source_type": str(attrs.get("source_type") or "unknown"),
                "server": attrs.get("server"),
                "database": attrs.get("database"),
                "value": attrs.get("value"),
                "provider": attrs.get("provider"),
            }
        )

    # Stable ordering for deterministic output/diffs.
    return sorted(
        out,
        key=lambda d: (
            str(d.get("source_type") or ""),
            str(d.get("provider") or ""),
            str(d.get("server") or ""),
            str(d.get("database") or ""),
            str(d.get("value") or ""),
            str(d.get("key") or ""),
            str(d.get("id") or ""),
        ),
    )


def summarize_sources(graph: WorkbookGraph) -> dict[str, Any]:
    """Summarize discovered sources.

    Intended for QA / quick inspection of whether a workbook's upstream data
    dependencies were discovered.
    """

    sources = list_sources(graph)
    by_type = Counter(str(s.get("source_type") or "unknown") for s in sources)
    by_provider = Counter(str(s.get("provider") or "") for s in sources)

    # Keep empty provider out of the summary unless it is the only value.
    if "" in by_provider and len(by_provider) > 1:
        by_provider.pop("", None)

    return {
        "sources": sources,
        "counts": {
            "total": len(sources),
            "by_type": dict(sorted(by_type.items())),
            "by_provider": dict(sorted(by_provider.items())),
        },
    }


def list_connections(graph: WorkbookGraph) -> list[dict[str, Any]]:
    """Return a stable, JSON-friendly list of discovered connections."""

    out: list[dict[str, Any]] = []
    for node in graph.nodes.values():
        if node.kind != "connection":
            continue
        attrs = dict(node.attrs)
        out.append(
            {
                "id": node.id,
                "key": node.key,
                "name": attrs.get("name"),
                "connection_kind": attrs.get("connection_kind"),
                "connection_id": attrs.get("connection_id"),
                "external_link_target": attrs.get("external_link_target"),
                "url": attrs.get("url"),
                "source_file": attrs.get("source_file"),
                "odc_file": attrs.get("odc_file"),
                "connection_summary": attrs.get("connection_summary"),
                "provider": attrs.get("provider"),
            }
        )

    return sorted(
        out,
        key=lambda d: (
            str(d.get("name") or ""),
            str(d.get("connection_kind") or ""),
            str(d.get("connection_id") or ""),
            str(d.get("key") or ""),
            str(d.get("id") or ""),
        ),
    )


def summarize_connections(graph: WorkbookGraph) -> dict[str, Any]:
    """Summarize connections and their links to sources.

    This is aimed at QA: if you suspect "connections exist but sources were missed",
    this will show which connections have `uses_source` edges.
    """

    connections = list_connections(graph)
    conn_ids = {c["id"] for c in connections}

    # Build connection -> source edges map.
    uses_source: dict[str, list[str]] = {cid: [] for cid in conn_ids}
    for e in graph.edges:
        if e.kind != "uses_source":
            continue
        if e.src in uses_source:
            uses_source[e.src].append(e.dst)

    for cid, dsts in uses_source.items():
        dsts.sort()

    by_kind = Counter(str(c.get("connection_kind") or "unknown") for c in connections)
    connected = sum(1 for cid, dsts in uses_source.items() if dsts)

    return {
        "connections": connections,
        "uses_source": uses_source,
        "counts": {
            "total": len(connections),
            "connected_to_sources": connected,
            "by_kind": dict(sorted(by_kind.items())),
        },
    }
