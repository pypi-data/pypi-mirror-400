from __future__ import annotations

"""Post-processing to distill and prune extracted workbook artifacts."""

import re
from dataclasses import dataclass
from typing import Any

from excelminer.backends.base import AnalysisContext, BackendReport
from excelminer.model.entities import (
    DefinedName,
    Entity,
    FormulaCell,
    FormulaGroup,
    Sheet,
)
from excelminer.model.graph import WorkbookGraph
from excelminer.rationalization.formulas import (
    abstract_formula_for_entry,
    abstract_formulas,
    clear_caches,
)


@dataclass(slots=True)
class DistillationStats:
    """Accumulates counts of created/removed artifacts during distillation."""

    formula_cells_seen: int = 0
    formula_groups_created: int = 0
    defined_names_seen: int = 0
    defined_names_removed: int = 0


_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_\.]*")


def _sheet_key(name: str) -> str:
    """Normalize sheet names for stable keys."""
    return re.sub(r"\s+", " ", (name or "").strip())


def _iter_nodes_by_kind(graph: WorkbookGraph, kind: str) -> list[Entity]:
    """Return graph nodes filtered by kind."""
    return [n for n in graph.nodes.values() if n.kind == kind]


def _extract_defined_name_names(graph: WorkbookGraph) -> dict[str, str]:
    """Return mapping defined_name_id -> lowercased defined name."""

    out: dict[str, str] = {}
    for n in _iter_nodes_by_kind(graph, "defined_name"):
        name = str(n.attrs.get("name") or "").strip()
        if name:
            out[n.id] = name.lower()
    return out


def _scan_formula_text_for_name_usage(
    formula: str,
    names_lower: set[str],
    token_cache: dict[str, set[str]] | None = None,
) -> set[str]:
    """Return the subset of defined names referenced in a formula string."""
    if not formula or not names_lower:
        return set()
    if token_cache is not None and formula in token_cache:
        toks = token_cache[formula]
    else:
        # Token scan is robust to many Excel formula forms.
        toks = {t.lower() for t in _TOKEN_RE.findall(formula)}
        if token_cache is not None:
            token_cache[formula] = toks
    return toks & names_lower


def _prune_unused_defined_names(graph: WorkbookGraph) -> int:
    """Remove defined names that are not referenced by any formula."""
    dn_id_to_name = _extract_defined_name_names(graph)
    if not dn_id_to_name:
        return 0

    names_lower = set(dn_id_to_name.values())
    used_lower: set[str] = set()
    token_cache: dict[str, set[str]] = {}
    used_ids: set[str] = {
        e.dst
        for e in graph.edges
        if e.kind == "uses_defined_name" and e.dst in dn_id_to_name
    }
    used_lower |= {dn_id_to_name[dn_id] for dn_id in used_ids}

    for n in _iter_nodes_by_kind(graph, "formula_cell"):
        formula = str(n.attrs.get("formula") or "")
        used_lower |= _scan_formula_text_for_name_usage(
            formula, names_lower, token_cache
        )

    unused_ids = [dn_id for dn_id, nm in dn_id_to_name.items() if nm not in used_lower]
    return graph.remove_nodes(unused_ids)


def _distill_formulas(graph: WorkbookGraph) -> int:
    """Group formula cells into FormulaGroup nodes and link to sheets."""
    formula_nodes = [n for n in graph.nodes.values() if n.kind == "formula_cell"]
    if not formula_nodes:
        return 0

    # Group by abstract formula per sheet.
    entries: list[dict[str, Any]] = []
    for n in formula_nodes:
        entries.append(
            {
                "sheet": n.attrs.get("sheet", "") or "",
                "address": n.attrs.get("address", "") or "",
                "formula": n.attrs.get("formula", "") or "",
                "deps": n.attrs.get("deps") or {},
            }
        )

    groups = abstract_formulas(entries, keep_members=False, include_ref_hints=True)

    created = 0
    for g in groups:
        sheet_name = str(g.get("sheet") or "")
        abstract_formula = str(g.get("abstract_formula") or "")
        count = int(g.get("count") or 0)
        address_ranges = list(g.get("address_ranges") or [])

        hint_block = {
            k: v for k, v in g.items() if k in ("ref_hints", "ref_hints_vary")
        }

        key = f"{_sheet_key(sheet_name)}|{abstract_formula}"
        ent = FormulaGroup.make(
            key=key,
            id=f"fgroup:{key}",
            sheet_name=sheet_name,
            abstract_formula=abstract_formula,
            count=count,
            address_ranges=address_ranges,
            ref_hints=hint_block.get("ref_hints"),
            ref_hints_vary=hint_block.get("ref_hints_vary"),
        )
        group_node = graph.upsert(ent)
        created += 1

        # Ensure sheet exists and attach the group as a contained artifact.
        sk = _sheet_key(sheet_name)
        if sk:
            sheet_node = graph.get_by_key("sheet", sk)
            if sheet_node is None:
                sheet_node = graph.upsert(
                    Sheet.make(key=sk, id=f"sheet:{sk}", name=sheet_name)
                )
            graph.add_edge(sheet_node.id, group_node.id, "contains")

    return created


def _link_formula_members(
    graph: WorkbookGraph, abstract_by_id: dict[str, tuple[str, str]]
) -> int:
    """Create member_of edges from formula_cell -> formula_group."""

    # Build a lookup of (sheet, abstract_formula) -> formula_group id
    group_lookup: dict[tuple[str, str], str] = {}
    for n in graph.nodes.values():
        if n.kind != "formula_group":
            continue
        sheet = str(n.attrs.get("sheet") or "")
        abstract = str(n.attrs.get("abstract_formula") or "")
        group_lookup[(sheet, abstract)] = n.id

    added = 0
    for fid, (sheet, abstract) in abstract_by_id.items():
        gid = group_lookup.get((sheet, abstract))
        if not gid:
            continue
        graph.add_edge(fid, gid, "member_of")
        added += 1
    return added


def distill_graph(ctx: AnalysisContext, graph: WorkbookGraph) -> BackendReport:
    """Optional post-analysis distillation/rationalization.

    This runs after extraction backends, and may:
      - add condensed summary artifacts (e.g., formula groups)
      - prune unused artifacts (e.g., unused defined names)

    It is opt-in via AnalysisOptions.post_analysis_distillation.
    """

    report = BackendReport(backend="distillation")
    stats = DistillationStats()

    stats.formula_cells_seen = len(_iter_nodes_by_kind(graph, "formula_cell"))
    stats.defined_names_seen = len(_iter_nodes_by_kind(graph, "defined_name"))

    try:
        # Precompute abstract formulas once, group, then link members.
        formula_nodes = [n for n in graph.nodes.values() if n.kind == "formula_cell"]
        abstract_by_id: dict[str, tuple[str, str]] = {}
        for n in formula_nodes:
            sheet_name = str(n.attrs.get("sheet", "") or "")
            formula = str(n.attrs.get("formula", "") or "")
            deps = n.attrs.get("deps") or {}
            abstract = abstract_formula_for_entry(
                sheet=sheet_name, formula=formula, deps=deps
            )
            abstract_by_id[n.id] = (sheet_name, abstract)

        stats.formula_groups_created = _distill_formulas(graph)
        _link_formula_members(graph, abstract_by_id)
    except Exception as e:  # noqa: BLE001
        report.add_issue(f"formula distillation failed: {e}", kind="runtime")

    try:
        stats.defined_names_removed = _prune_unused_defined_names(graph)
    except Exception as e:  # noqa: BLE001
        report.add_issue(f"defined-name pruning failed: {e}", kind="runtime")

    report.stats = {
        **graph.stats(),
        "distill_formula_cells_seen": stats.formula_cells_seen,
        "distill_formula_groups_created": stats.formula_groups_created,
        "distill_defined_names_seen": stats.defined_names_seen,
        "distill_defined_names_removed": stats.defined_names_removed,
    }

    # Clear LRU caches used by rationalization helpers to avoid retaining memory
    # after the optional distillation step.
    try:
        clear_caches()
    except Exception:
        pass
    return report
