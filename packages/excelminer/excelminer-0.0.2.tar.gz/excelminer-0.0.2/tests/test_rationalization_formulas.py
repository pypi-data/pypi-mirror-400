from __future__ import annotations

from excelminer.rationalization.formulas import abstract_formulas, collapse_ranges


def test_collapse_ranges_collapses_vertical_runs() -> None:
    assert collapse_ranges(["A1", "A2", "A3"]) == ["A1:A3"]
    assert collapse_ranges(["B2", "B4", "B3"]) == ["B2:B4"]


def test_collapse_ranges_separates_columns() -> None:
    # Only collapses contiguous rows within the same column.
    out = collapse_ranges(["A1", "A2", "B1", "B2", "B4"])
    assert out == ["A1:A2", "B1:B2", "B4"]


def test_abstract_formulas_groups_dragged_formulas_with_relative_consistent_hints() -> (
    None
):
    entries = [
        {
            "sheet": "Data",
            "address": "A1",
            "formula": "=B1+C1",
            "deps": {
                "refs": [{"sheet": "", "cell": "B1"}, {"sheet": "", "cell": "C1"}]
            },
        },
        {
            "sheet": "Data",
            "address": "A2",
            "formula": "=B2+C2",
            "deps": {
                "refs": [{"sheet": "", "cell": "B2"}, {"sheet": "", "cell": "C2"}]
            },
        },
    ]

    groups = abstract_formulas(entries, keep_members=False, include_ref_hints=True)
    assert len(groups) == 1

    g = groups[0]
    assert g["sheet"] == "Data"
    assert g["count"] == 2
    assert g["abstract_formula"] == "=|ref1|+|ref2|"

    assert g.get("ref_hints_vary") is False
    ref_hints = g.get("ref_hints")
    assert isinstance(ref_hints, dict)
    assert ref_hints["ref1"]["kind"] == "relative"
    assert ref_hints["ref2"]["kind"] == "relative"


def test_abstract_formulas_handles_quoted_sheet_refs() -> None:
    entries = [
        {
            "sheet": "Current",
            "address": "A1",
            "formula": "='Other Sheet'!$B$2 + 1",
            "deps": {"refs": [{"sheet": "Other Sheet", "cell": "B2"}]},
        }
    ]

    groups = abstract_formulas(entries, keep_members=False, include_ref_hints=False)
    assert len(groups) == 1
    assert groups[0]["abstract_formula"] == "=|ref1| + 1"


def test_abstract_formulas_marks_varying_refs_when_truly_inconsistent() -> None:
    # Same sheet + same formula cell address, but deps point to different absolute cells.
    entries = [
        {
            "sheet": "Data",
            "address": "A1",
            "formula": "=$B$1",
            "deps": {"refs": [{"sheet": "", "cell": "B1"}]},
        },
        {
            "sheet": "Data",
            "address": "A1",
            "formula": "=$B$2",
            "deps": {"refs": [{"sheet": "", "cell": "B2"}]},
        },
    ]

    groups = abstract_formulas(entries, keep_members=False, include_ref_hints=True)
    assert len(groups) == 1

    g = groups[0]
    assert g["abstract_formula"] == "=|ref1|"
    assert g.get("ref_hints_vary") is True
    ref1 = g["ref_hints"]["ref1"]
    assert ref1["varies_across_members"] is True
