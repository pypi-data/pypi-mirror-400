from __future__ import annotations

"""Graph entity definitions for workbook artifacts."""

from dataclasses import dataclass, field
from typing import Any, Literal


# -----------------------------
# Core graph primitives
# -----------------------------
@dataclass(frozen=True, slots=True)
class Edge:
    """A directed edge between two entities."""

    src: str
    dst: str
    kind: str
    attrs: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the edge to a JSON-friendly dictionary."""
        return {
            "src": self.src,
            "dst": self.dst,
            "kind": self.kind,
            "attrs": dict(self.attrs),
        }


@dataclass(frozen=True, slots=True)
class Entity:
    """Base entity for the workbook graph.

    - kind: category string ("source", "connection", "sheet", ...)
    - id: stable ID string used throughout the graph (e.g. "src:sqlserver|host|db")
    - key: dedupe key (unique *within kind*); graph uses (kind, key) to de-duplicate
    - attrs: flexible payload
    """

    kind: str
    id: str
    key: str
    attrs: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the entity to a JSON-friendly dictionary."""
        return {
            "kind": self.kind,
            "id": self.id,
            "key": self.key,
            "attrs": dict(self.attrs),
        }


# -----------------------------
# Typed entities (thin wrappers)
# -----------------------------
SourceType = Literal[
    "sqlserver",
    "postgresql",
    "oracle",
    "odbc_dsn",
    "web",
    "file",
    "sharepoint",
    "unknown",
]


@dataclass(frozen=True, slots=True)
class Source(Entity):
    source_type: SourceType = "unknown"

    @staticmethod
    def make(
        *,
        source_type: SourceType,
        key: str,
        id: str,
        server: str | None = None,
        database: str | None = None,
        value: str | None = None,
        provider: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> "Source":
        """Build a Source entity with common attributes filled in."""
        attrs: dict[str, Any] = {"source_type": source_type}
        if server:
            attrs["server"] = server
        if database:
            attrs["database"] = database
        if value:
            attrs["value"] = value
        if provider:
            attrs["provider"] = provider
        if extra:
            attrs.update(extra)
        return Source(
            kind="source", id=id, key=key, attrs=attrs, source_type=source_type
        )


ConnectionKind = Literal[
    "oledb",
    "odbc",
    "text",
    "web",
    "powerquery",
    "datamodel",
    "worksheet",
    "unknown",
]


@dataclass(frozen=True, slots=True)
class Connection(Entity):
    connection_kind: ConnectionKind = "unknown"

    @staticmethod
    def make(
        *,
        key: str,
        id: str,
        name: str,
        connection_kind: ConnectionKind = "unknown",
        raw: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> "Connection":
        """Build a Connection entity with parsed attributes."""
        attrs: dict[str, Any] = {"name": name, "connection_kind": connection_kind}
        if raw is not None:
            attrs["raw"] = raw
        if details:
            attrs.update(details)
        return Connection(
            kind="connection",
            id=id,
            key=key,
            attrs=attrs,
            connection_kind=connection_kind,
        )


@dataclass(frozen=True, slots=True)
class PowerQuery(Entity):
    @staticmethod
    def make(
        *,
        key: str,
        id: str,
        name: str,
        m_code: str | None = None,
        script_count: int | None = None,
        script_names: list[str] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> "PowerQuery":
        """Build a PowerQuery entity with optional M code and extras."""
        attrs: dict[str, Any] = {"name": name}
        if m_code is not None:
            attrs["m_code"] = m_code
        if script_count is not None:
            attrs["script_count"] = script_count
        if script_names:
            attrs["script_names"] = list(script_names)
        if extra:
            attrs.update(extra)
        return PowerQuery(kind="powerquery", id=id, key=key, attrs=attrs)


@dataclass(frozen=True, slots=True)
class MScript(Entity):
    @staticmethod
    def make(
        *,
        key: str,
        id: str,
        name: str,
        m_code: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> "MScript":
        """Build an M script entity with optional code payload."""
        attrs: dict[str, Any] = {"name": name}
        if m_code is not None:
            attrs["m_code"] = m_code
        if extra:
            attrs.update(extra)
        return MScript(kind="m_script", id=id, key=key, attrs=attrs)


PivotSourceType = Literal[
    "connection", "worksheet", "table", "consolidation", "unknown"
]


@dataclass(frozen=True, slots=True)
class PivotCache(Entity):
    @staticmethod
    def make(
        *,
        key: str,
        id: str,
        cache_id: str,
        source_type: PivotSourceType,
        source_ref: str,
        extra: dict[str, Any] | None = None,
    ) -> "PivotCache":
        """Build a PivotCache entity with source metadata."""
        attrs: dict[str, Any] = {
            "cache_id": cache_id,
            "source_type": source_type,
            "source_reference": source_ref,
        }
        if extra:
            attrs.update(extra)
        return PivotCache(kind="pivot_cache", id=id, key=key, attrs=attrs)


@dataclass(frozen=True, slots=True)
class PivotTable(Entity):
    @staticmethod
    def make(
        *,
        key: str,
        id: str,
        name: str,
        sheet_name: str,
        measures: list[dict[str, Any]] | None = None,
        grouping_fields: list[dict[str, Any]] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> "PivotTable":
        """Build a PivotTable entity with measures and grouping fields."""
        attrs: dict[str, Any] = {"name": name, "sheet": sheet_name}
        if measures is not None:
            attrs["measures"] = measures
        if grouping_fields is not None:
            attrs["grouping_fields"] = grouping_fields
        if extra:
            attrs.update(extra)
        return PivotTable(kind="pivot_table", id=id, key=key, attrs=attrs)


@dataclass(frozen=True, slots=True)
class Chart(Entity):
    @staticmethod
    def make(
        *,
        key: str,
        id: str,
        name: str,
        extra: dict[str, Any] | None = None,
    ) -> "Chart":
        """Build a Chart entity."""
        attrs: dict[str, Any] = {"name": name}
        if extra:
            attrs.update(extra)
        return Chart(kind="chart", id=id, key=key, attrs=attrs)


@dataclass(frozen=True, slots=True)
class Sheet(Entity):
    @staticmethod
    def make(
        *,
        key: str,
        id: str,
        name: str,
        index: int | None = None,
        extra: dict[str, Any] | None = None,
    ) -> "Sheet":
        """Build a Sheet entity."""
        attrs: dict[str, Any] = {"name": name}
        if index is not None:
            attrs["index"] = index
        if extra:
            attrs.update(extra)
        return Sheet(kind="sheet", id=id, key=key, attrs=attrs)


@dataclass(frozen=True, slots=True)
class DefinedName(Entity):
    @staticmethod
    def make(
        *,
        key: str,
        id: str,
        name: str,
        scope: str,
        refers_to: str,
        extra: dict[str, Any] | None = None,
    ) -> "DefinedName":
        """Build a DefinedName entity scoped to a sheet or workbook."""
        attrs: dict[str, Any] = {"name": name, "scope": scope, "refers_to": refers_to}
        if extra:
            attrs.update(extra)
        return DefinedName(kind="defined_name", id=id, key=key, attrs=attrs)


CellBlockType = Literal["value_block", "table", "named_range", "unknown"]


@dataclass(frozen=True, slots=True)
class CellBlock(Entity):
    @staticmethod
    def make(
        *,
        key: str,
        id: str,
        sheet_name: str,
        a1_range: str,
        block_type: CellBlockType,
        stats: dict[str, Any] | None = None,
        sample: list[list[Any]] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> "CellBlock":
        """Build a CellBlock entity describing a rectangular used range."""
        attrs: dict[str, Any] = {
            "sheet": sheet_name,
            "range": a1_range,
            "block_type": block_type,
        }
        if stats:
            attrs["stats"] = stats
        if sample:
            attrs["sample"] = sample
        if extra:
            attrs.update(extra)
        return CellBlock(kind="cell_block", id=id, key=key, attrs=attrs)


@dataclass(frozen=True, slots=True)
class FormulaCell(Entity):
    @staticmethod
    def make(
        *,
        key: str,
        id: str,
        sheet_name: str,
        address: str,
        formula: str,
        deps: dict[str, Any] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> "FormulaCell":
        """Build a FormulaCell entity with dependency hints."""
        attrs: dict[str, Any] = {
            "sheet": sheet_name,
            "address": address,
            "formula": formula,
        }
        if deps:
            attrs["deps"] = deps
        if extra:
            attrs.update(extra)
        return FormulaCell(kind="formula_cell", id=id, key=key, attrs=attrs)


@dataclass(frozen=True, slots=True)
class FormulaGroup(Entity):
    @staticmethod
    def make(
        *,
        key: str,
        id: str,
        sheet_name: str,
        abstract_formula: str,
        count: int,
        address_ranges: list[str] | None = None,
        ref_hints: dict[str, Any] | None = None,
        ref_hints_vary: bool | None = None,
        extra: dict[str, Any] | None = None,
    ) -> "FormulaGroup":
        """Build a FormulaGroup entity summarizing repeated formulas."""
        attrs: dict[str, Any] = {
            "sheet": sheet_name,
            "abstract_formula": abstract_formula,
            "count": int(count),
        }
        if address_ranges is not None:
            attrs["address_ranges"] = list(address_ranges)
        if ref_hints is not None:
            attrs["ref_hints"] = dict(ref_hints)
        if ref_hints_vary is not None:
            attrs["ref_hints_vary"] = bool(ref_hints_vary)
        if extra:
            attrs.update(extra)
        return FormulaGroup(kind="formula_group", id=id, key=key, attrs=attrs)
