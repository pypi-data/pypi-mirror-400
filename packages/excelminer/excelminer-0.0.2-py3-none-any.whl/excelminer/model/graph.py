from __future__ import annotations

"""Workbook graph container and helper methods."""

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

from .entities import Edge, Entity


@dataclass(slots=True)
class WorkbookGraph:
    """In-memory normalized graph of workbook artifacts.

    - Nodes are de-duped by (kind, key).
    - Edges are free-form but should use stable 'kind' values.
    """

    nodes: dict[str, Entity] = field(default_factory=dict)  # id -> entity
    edges: list[Edge] = field(default_factory=list)
    node_sinks: list[Callable[[Entity], None]] = field(default_factory=list, repr=False)
    edge_sinks: list[Callable[[Edge], None]] = field(default_factory=list, repr=False)

    # (kind, key) -> id
    _index: dict[tuple[str, str], str] = field(default_factory=dict)

    def register_node_sink(self, sink: Callable[[Entity], None]) -> None:
        """Register a callback invoked when a new node is inserted."""
        self.node_sinks.append(sink)

    def register_edge_sink(self, sink: Callable[[Edge], None]) -> None:
        """Register a callback invoked when a new edge is inserted."""
        self.edge_sinks.append(sink)

    def _notify_node_sinks(self, entity: Entity) -> None:
        for sink in self.node_sinks:
            sink(entity)

    def _notify_edge_sinks(self, edge: Edge) -> None:
        for sink in self.edge_sinks:
            sink(edge)

    # ---------- Node ops ----------
    def upsert(self, entity: Entity) -> Entity:
        """Insert entity if (kind, key) not present; otherwise return existing.

        If same (kind, key) exists but with different id, keeps the original id.
        """

        idx_key = (entity.kind, entity.key)
        existing_id = self._index.get(idx_key)
        if existing_id:
            return self.nodes[existing_id]

        self._index[idx_key] = entity.id
        self.nodes[entity.id] = entity
        self._notify_node_sinks(entity)
        return entity

    def add_nodes(self, nodes: Iterable[Entity]) -> None:
        """Insert multiple nodes without buffering them in memory."""
        for entity in nodes:
            self.upsert(entity)

    def get(self, entity_id: str) -> Entity | None:
        """Return the entity by id if present."""
        return self.nodes.get(entity_id)

    def get_by_key(self, kind: str, key: str) -> Entity | None:
        """Return an entity by (kind, key) if present."""
        entity_id = self._index.get((kind, key))
        return self.nodes.get(entity_id) if entity_id else None

    def get_or_create(
        self, kind: str, key: str, factory: Callable[[], Entity]
    ) -> Entity:
        """Return an entity if it exists, otherwise create and insert one."""
        existing = self.get_by_key(kind, key)
        if existing:
            return existing
        return self.upsert(factory())

    # ---------- Edge ops ----------
    def add_edge(self, src: str, dst: str, kind: str, **attrs: Any) -> Edge:
        """Create and append a new edge between existing nodes."""
        if src not in self.nodes:
            raise KeyError(f"edge src node not found: {src}")
        if dst not in self.nodes:
            raise KeyError(f"edge dst node not found: {dst}")
        e = Edge(src=src, dst=dst, kind=kind, attrs=dict(attrs))
        self.edges.append(e)
        self._notify_edge_sinks(e)
        return e

    def add_edges(self, edges: Iterable[Edge]) -> None:
        """Append multiple edges, validating endpoints exist."""
        for e in edges:
            if e.src not in self.nodes:
                raise KeyError(f"edge src node not found: {e.src}")
            if e.dst not in self.nodes:
                raise KeyError(f"edge dst node not found: {e.dst}")
            self.edges.append(e)
            self._notify_edge_sinks(e)

    def __len__(self) -> int:
        """Return number of nodes in the graph."""
        return len(self.nodes)

    def __repr__(self) -> str:
        # Keep notebook display safe: do not dump nodes/edges by default.
        return f"WorkbookGraph(nodes={len(self.nodes)}, edges={len(self.edges)})"

    def __contains__(self, entity_id: str) -> bool:
        """Return True if an entity id exists in the graph."""
        return entity_id in self.nodes

    def _sorted_nodes(self) -> list[Entity]:
        """Return nodes in stable order for deterministic output."""
        # Stable output for JSON serialization and diffs.
        return sorted(self.nodes.values(), key=lambda n: (n.kind, n.key, n.id))

    def _sorted_edges(self) -> list[Edge]:
        """Return edges in stable order for deterministic output."""
        return sorted(self.edges, key=lambda e: (e.kind, e.src, e.dst))

    # ---------- Serialization ----------
    def to_dict(self) -> dict[str, Any]:
        """Serialize the graph to a JSON-friendly dictionary."""
        return {
            "nodes": [n.to_dict() for n in self._sorted_nodes()],
            "edges": [e.to_dict() for e in self._sorted_edges()],
            "stats": self.stats(),
        }

    # ---------- Convenience ----------
    def stats(self) -> dict[str, int]:
        """Return counts of nodes/edges and node kinds."""
        by_kind: dict[str, int] = {}
        for n in self.nodes.values():
            by_kind[n.kind] = by_kind.get(n.kind, 0) + 1
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            **{f"nodes_{k}": v for k, v in by_kind.items()},
        }

    # ---------- Mutations / pruning ----------
    def remove_nodes(self, entity_ids: Iterable[str]) -> int:
        """Remove nodes and any incident edges.

        Returns the number of nodes removed.
        """

        to_remove = {eid for eid in entity_ids if eid in self.nodes}
        if not to_remove:
            return 0

        # Drop edges touching removed nodes.
        self.edges = [
            e for e in self.edges if (e.src not in to_remove and e.dst not in to_remove)
        ]

        removed = 0
        for eid in to_remove:
            ent = self.nodes.pop(eid, None)
            if ent is None:
                continue
            removed += 1
            idx_key = (ent.kind, ent.key)
            if self._index.get(idx_key) == eid:
                self._index.pop(idx_key, None)

        return removed
