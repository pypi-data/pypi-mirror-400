from __future__ import annotations

"""Formula rationalization helpers for grouping and abstraction."""

import re
from collections import defaultdict
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

# -----------------------------
# A1 helpers
# -----------------------------
_A1_RE = re.compile(r"^\$?([A-Z]{1,3})\$?(\d+)$", re.IGNORECASE)


@lru_cache(maxsize=2048)
def _col_to_int(col: str) -> int:
    """Convert Excel column letters to a 1-based index."""
    col = col.upper()
    n = 0
    for ch in col:
        n = n * 26 + (ord(ch) - ord("A") + 1)
    return n


@lru_cache(maxsize=2048)
def _int_to_col(n: int) -> str:
    """Convert a 1-based column index to Excel letters."""
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(r + ord("A")) + s
    return s


def clear_caches() -> None:
    """Clear LRU caches used for A1 conversions."""
    _col_to_int.cache_clear()
    _int_to_col.cache_clear()


def _parse_a1(addr: str) -> Optional[Tuple[int, int]]:
    """Parse A1 notation into (col_index, row_index)."""
    m = _A1_RE.match((addr or "").strip())
    if not m:
        return None
    col, row = m.group(1), int(m.group(2))
    return (_col_to_int(col), row)


def _parse_a1_parts(addr: str) -> Optional[Tuple[str, int]]:
    """Parse A1 notation into (column_letters, row_index)."""
    m = _A1_RE.match((addr or "").strip())
    if not m:
        return None
    return (m.group(1).upper(), int(m.group(2)))


def _cell_ref_regex(cell: str) -> Optional[str]:
    """Build a regex fragment that matches an A1 cell reference."""
    if not cell:
        return None
    m = _A1_RE.match((cell or "").replace("$", "").strip())
    if not m:
        return None
    col, row = m.group(1).upper(), m.group(2)
    return rf"\$?{re.escape(col)}\$?{re.escape(row)}"


def _sheet_token_variants(sheet: str) -> List[str]:
    """Return quoted and unquoted sheet token variants."""
    sheet = (sheet or "").strip()
    if not sheet:
        return []
    unquoted = (
        sheet[1:-1]
        if (len(sheet) >= 2 and sheet[0] == "'" and sheet[-1] == "'")
        else sheet
    )
    return [f"'{unquoted}'", unquoted]


def _same_sheet(ref_sheet: str, current_sheet: str) -> bool:
    """Return True if the reference sheet is empty or matches the current sheet."""
    rs = (ref_sheet or "").strip()
    cs = (current_sheet or "").strip()
    if not rs:
        return True
    return rs.strip("'").lower() == cs.strip("'").lower()


def _ref_patterns(ref_sheet: str, ref_cell: str, current_sheet: str) -> List[str]:
    """Generate regex patterns for matching cell references in formulas."""
    cell_rx = _cell_ref_regex(ref_cell)
    if not cell_rx:
        return []

    ref_sheet = (ref_sheet or "").strip()
    current_sheet = (current_sheet or "").strip()

    pats: List[str] = []

    if not ref_sheet:
        pats.append(rf"(?<![A-Z0-9_]){cell_rx}(?![A-Z0-9_])")
        return pats

    for sht in _sheet_token_variants(ref_sheet):
        pats.append(re.escape(sht + "!") + cell_rx)

    if ref_sheet.strip("'").lower() == current_sheet.strip("'").lower():
        pats.append(rf"(?<![A-Z0-9_]){cell_rx}(?![A-Z0-9_])")

    return pats


def _range_ref_regex(range_addr: str) -> Optional[str]:
    """Build a regex fragment that matches an A1 range reference."""
    if not range_addr or ":" not in range_addr:
        return None
    start, end = (part.strip() for part in range_addr.split(":", 1))
    start_rx = _cell_ref_regex(start)
    end_rx = _cell_ref_regex(end)
    if not (start_rx and end_rx):
        return None
    return f"{start_rx}:{end_rx}"


def _external_sheet_variants(workbook: str, sheet: str) -> List[str]:
    """Return quoted and unquoted external sheet tokens."""
    wb = (workbook or "").strip()
    sh = (sheet or "").strip()
    if not wb or not sh:
        return []
    base = f"[{wb}]{sh}"
    return [f"'{base}'", base]


def _ref_kind(ref: Dict[str, Any]) -> str:
    """Return normalized reference kind based on available fields."""
    if ref.get("kind"):
        return str(ref["kind"])
    if ref.get("workbook"):
        return "external"
    if ref.get("range"):
        return "range"
    if ref.get("structured"):
        return "structured"
    if ref.get("name"):
        return "name"
    if ref.get("cell"):
        return "cell"
    return "unknown"


def _ref_patterns_for_ref(ref: Dict[str, Any], current_sheet: str) -> List[str]:
    """Generate regex patterns for matching a reference entry in formulas."""
    kind = _ref_kind(ref)

    if kind == "cell":
        return _ref_patterns(ref.get("sheet", ""), ref.get("cell", ""), current_sheet)

    if kind == "range":
        range_rx = _range_ref_regex(ref.get("range", ""))
        if not range_rx:
            return []
        ref_sheet = (ref.get("sheet") or "").strip()
        current_sheet = (current_sheet or "").strip()
        pats: List[str] = []

        if not ref_sheet:
            pats.append(rf"(?<![A-Z0-9_]){range_rx}(?![A-Z0-9_])")
            return pats

        for sht in _sheet_token_variants(ref_sheet):
            pats.append(re.escape(sht + "!") + range_rx)

        if ref_sheet.strip("'").lower() == current_sheet.strip("'").lower():
            pats.append(rf"(?<![A-Z0-9_]){range_rx}(?![A-Z0-9_])")

        return pats

    if kind == "external":
        workbook = ref.get("workbook", "")
        sheet = ref.get("sheet", "")
        range_rx = _range_ref_regex(ref.get("range", ""))
        cell_rx = _cell_ref_regex(ref.get("cell", ""))
        target_rx = range_rx or cell_rx
        if not target_rx:
            return []
        return [
            re.escape(token + "!") + target_rx
            for token in _external_sheet_variants(workbook, sheet)
        ]

    if kind == "structured":
        structured = (ref.get("structured") or "").strip()
        if not structured:
            return []
        return [re.escape(structured)]

    if kind == "name":
        name = (ref.get("name") or "").strip()
        if not name:
            return []
        return [rf"(?<![A-Z0-9_.]){re.escape(name)}(?![A-Z0-9_.]|\s*\()"]

    return []


def _ref_hint_for_member(
    member_sheet: str,
    member_address: str,
    ref_sheet: str,
    ref_cell: str,
) -> Optional[Dict[str, Any]]:
    """Return reference hint metadata for a single formula member."""
    ref_cell = (ref_cell or "").strip()
    if not ref_cell:
        return None

    out: Dict[str, Any] = {"sheet": (ref_sheet or "").strip(), "cell": ref_cell}

    if not _same_sheet(ref_sheet, member_sheet):
        return out

    a = _parse_a1(member_address)
    r = _parse_a1(ref_cell)
    ap = _parse_a1_parts(member_address)
    rp = _parse_a1_parts(ref_cell)
    if not (a and r and ap and rp):
        return out

    a_col, a_row = a
    r_col, r_row = r
    dc = r_col - a_col
    dr = r_row - a_row

    ref_col_letters, _ = rp
    sign = "+" if dr >= 0 else "-"
    out["relative"] = f"{ref_col_letters}[row{sign}{abs(dr)}]"
    out["r1c1"] = f"R[{dr}]C[{dc}]"
    out["offset"] = {"dr": dr, "dc": dc}
    return out


# -----------------------------
# Grouping helpers
# -----------------------------
def collapse_ranges(addresses: List[str]) -> List[str]:
    """Collapse a list of A1 addresses into minimal contiguous ranges."""
    parsed = []
    for a in addresses:
        p = _parse_a1(a)
        if p:
            parsed.append((p[0], p[1], a))
    parsed.sort(key=lambda t: (t[0], t[1]))

    out = []
    i = 0
    while i < len(parsed):
        col, row, _ = parsed[i]
        start_row = row
        end_row = row
        j = i + 1
        while j < len(parsed) and parsed[j][0] == col and parsed[j][1] == end_row + 1:
            end_row = parsed[j][1]
            j += 1

        col_letters = _int_to_col(col)
        out.append(
            f"{col_letters}{start_row}"
            if start_row == end_row
            else f"{col_letters}{start_row}:{col_letters}{end_row}"
        )
        i = j
    return out


def _normalize_sheet_key(ref_sheet: str, current_sheet: str) -> str:
    """Normalize sheet names for cross-sheet reference comparison."""
    rs = (ref_sheet or "").strip()
    cs = (current_sheet or "").strip()

    rs_u = rs.strip("'")
    cs_u = cs.strip("'")

    if not rs_u:
        return ""
    if rs_u.lower() == cs_u.lower():
        return ""
    return rs_u


def _offset_desc(dr: int, dc: int) -> str:
    """Return a human-friendly description of row/column offsets."""
    parts = []
    if dr == 0:
        parts.append("same row")
    elif dr > 0:
        parts.append(f"{dr} rows down")
    else:
        parts.append(f"{abs(dr)} rows up")

    if dc == 0:
        parts.append("same column")
    elif dc > 0:
        parts.append(f"{dc} cols right")
    else:
        parts.append(f"{abs(dc)} cols left")

    return ", ".join(parts)


def consistent_ref_hints(
    sheet: str, members: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """Return consistent reference hints across a group of formula members."""
    abs_first: Dict[int, Tuple[str, str]] = {}
    abs_varies: Dict[int, bool] = defaultdict(bool)
    abs_example: Dict[int, Dict[str, Any]] = {}

    rel_first: Dict[int, Tuple[str, int, int]] = {}
    rel_varies: Dict[int, bool] = defaultdict(bool)
    rel_example: Dict[int, Dict[str, Any]] = {}

    unparseable_count: Dict[int, int] = defaultdict(int)
    seen_any: Dict[int, bool] = defaultdict(bool)

    for m in members:
        addr = (m.get("address") or "").strip()
        deps = m.get("deps") or {}
        refs = deps.get("refs") or []

        a = _parse_a1(addr)

        for i, r in enumerate(refs, start=1):
            r_kind = _ref_kind(r)
            if r_kind == "cell":
                r_sheet_raw = (r.get("sheet") or "").strip()
                r_cell_raw = (r.get("cell") or "").strip()
                if not r_cell_raw:
                    continue

                seen_any[i] = True
                sheet_key = _normalize_sheet_key(r_sheet_raw, sheet)

                r_cell_norm = r_cell_raw.replace("$", "").upper()
                abs_sig = ("cell", sheet_key, r_cell_norm)

                if i not in abs_first:
                    abs_first[i] = abs_sig
                    abs_example[i] = {
                        "kind": "absolute",
                        "ref_kind": "cell",
                        "sheet": sheet_key,
                        "cell": r_cell_norm,
                        "example": {
                            "from": addr,
                            "to": (
                                r_cell_norm
                                if not sheet_key
                                else f"{sheet_key}!{r_cell_norm}"
                            ),
                        },
                    }
                elif abs_first[i] != abs_sig:
                    abs_varies[i] = True

                r_parsed = _parse_a1(r_cell_raw)
                if not (a and r_parsed):
                    unparseable_count[i] += 1
                    continue

                a_col, a_row = a
                r_col, r_row = r_parsed
                dr = r_row - a_row
                dc = r_col - a_col

                rel_sig = (sheet_key, dr, dc)

                if i not in rel_first:
                    rel_first[i] = rel_sig
                    rel_example[i] = {
                        "kind": "relative",
                        "ref_kind": "cell",
                        "sheet": sheet_key,
                        "offset": {"dr": dr, "dc": dc},
                        "r1c1": f"R[{dr}]C[{dc}]",
                        "offset_desc": _offset_desc(dr, dc),
                        "example": {
                            "from": addr,
                            "to": (
                                r_cell_norm
                                if not sheet_key
                                else f"{sheet_key}!{r_cell_norm}"
                            ),
                        },
                    }
                elif rel_first[i] != rel_sig:
                    rel_varies[i] = True
                continue

            r_sheet_raw = (r.get("sheet") or "").strip()
            r_range_raw = (r.get("range") or "").strip()
            r_structured = (r.get("structured") or "").strip()
            r_name = (r.get("name") or "").strip()
            r_workbook = (r.get("workbook") or "").strip()

            if r_kind == "range" and not r_range_raw:
                continue
            if r_kind == "structured" and not r_structured:
                continue
            if r_kind == "name" and not r_name:
                continue
            if r_kind == "external" and not (
                r_workbook and (r.get("cell") or r_range_raw)
            ):
                continue

            seen_any[i] = True
            sheet_key = _normalize_sheet_key(r_sheet_raw, sheet)

            if r_kind == "range":
                r_range_norm = r_range_raw.replace("$", "").upper()
                abs_sig = ("range", sheet_key, r_range_norm)
                example_to = (
                    r_range_norm if not sheet_key else f"{sheet_key}!{r_range_norm}"
                )
                hint = {
                    "kind": "absolute",
                    "ref_kind": "range",
                    "sheet": sheet_key,
                    "range": r_range_norm,
                    "example": {"from": addr, "to": example_to},
                }
            elif r_kind == "structured":
                abs_sig = ("structured", r_structured)
                hint = {
                    "kind": "absolute",
                    "ref_kind": "structured",
                    "structured": r_structured,
                    "example": {"from": addr, "to": r_structured},
                }
            elif r_kind == "name":
                abs_sig = ("name", r_name)
                hint = {
                    "kind": "absolute",
                    "ref_kind": "name",
                    "name": r_name,
                    "example": {"from": addr, "to": r_name},
                }
            else:  # external
                r_cell_raw = (r.get("cell") or "").strip()
                r_cell_norm = r_cell_raw.replace("$", "").upper()
                r_range_norm = r_range_raw.replace("$", "").upper()
                target = r_range_norm or r_cell_norm
                abs_sig = ("external", r_workbook, r_sheet_raw, target)
                hint = {
                    "kind": "absolute",
                    "ref_kind": "external",
                    "workbook": r_workbook,
                    "sheet": r_sheet_raw,
                }
                if r_range_norm:
                    hint["range"] = r_range_norm
                if r_cell_norm:
                    hint["cell"] = r_cell_norm
                hint["example"] = {
                    "from": addr,
                    "to": f"[{r_workbook}]{r_sheet_raw}!{target}",
                }

            if i not in abs_first:
                abs_first[i] = abs_sig
                abs_example[i] = hint
            elif abs_first[i] != abs_sig:
                abs_varies[i] = True

    if not any(seen_any.values()):
        return None

    ref_hints: Dict[str, Any] = {}
    varies_any = False

    for i in sorted(seen_any.keys()):
        key = f"ref{i}"

        if i in abs_first and not abs_varies[i]:
            hint = dict(abs_example[i])
            if unparseable_count[i]:
                hint["note"] = (
                    f"{unparseable_count[i]} member(s) unparseable for relative offset"
                )
            ref_hints[key] = hint
            continue

        if i in rel_first and not rel_varies[i]:
            hint = dict(rel_example[i])
            if unparseable_count[i]:
                hint["note"] = (
                    f"{unparseable_count[i]} member(s) unparseable for relative offset"
                )
            ref_hints[key] = hint
            continue

        varies_any = True
        ref_hints[key] = {
            "varies_across_members": True,
            "absolute_varies": bool(abs_varies.get(i, False)),
            "relative_varies": bool(rel_varies.get(i, False)),
            "unparseable_members": unparseable_count.get(i, 0),
        }

    return {"ref_hints": ref_hints, "ref_hints_vary": varies_any}


# -----------------------------
# Main API
# -----------------------------


def abstract_formula_for_entry(
    *,
    sheet: str,
    formula: str,
    deps: dict[str, Any] | None,
    placeholder: str = "|ref{n}|",
) -> str:
    """Return an abstracted formula by replacing referenced cells."""
    deps = deps or {}
    refs = deps.get("refs") or []

    repl_specs: List[Tuple[str, str]] = []
    for i, r in enumerate(refs, start=1):
        ph = placeholder.format(n=i)
        for pat in _ref_patterns_for_ref(r, current_sheet=sheet):
            repl_specs.append((pat, ph))

    abstract = formula or ""
    for pat, ph in sorted(repl_specs, key=lambda t: len(t[0]), reverse=True):
        abstract = re.sub(pat, ph, abstract, flags=re.IGNORECASE)

    return abstract


def abstract_formulas(
    entries: List[Dict[str, Any]],
    placeholder: str = "|ref{n}|",
    keep_members: bool = False,
    include_ref_hints: bool = True,
) -> List[Dict[str, Any]]:
    """Group formulas by abstract form and return grouped metadata."""
    buckets: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)

    for e in entries:
        sheet = e.get("sheet", "") or ""
        formula = e.get("formula", "") or ""

        deps = e.get("deps") or {}

        abstract = abstract_formula_for_entry(
            sheet=sheet,
            formula=formula,
            deps=deps,
            placeholder=placeholder,
        )

        member_rec = (
            e
            if keep_members
            else {
                "address": e.get("address", ""),
                "deps": deps,
            }
        )

        buckets[(sheet, abstract)].append(member_rec)

    results: List[Dict[str, Any]] = []
    for (sheet, abstract_formula), members in buckets.items():
        addrs = [m.get("address", "") for m in members if m.get("address")]
        group: Dict[str, Any] = {
            "sheet": sheet,
            "abstract_formula": abstract_formula,
            "address_ranges": collapse_ranges(addrs),
            "count": len(members),
        }

        if include_ref_hints:
            hint_block = consistent_ref_hints(sheet, members)
            if hint_block:
                group.update(hint_block)

        if keep_members:
            group["members"] = members

        results.append(group)

    results.sort(key=lambda g: (-g["count"], g["sheet"], g["abstract_formula"]))
    return results


__all__ = [
    "abstract_formula_for_entry",
    "abstract_formulas",
    "collapse_ranges",
    "clear_caches",
    "consistent_ref_hints",
]
