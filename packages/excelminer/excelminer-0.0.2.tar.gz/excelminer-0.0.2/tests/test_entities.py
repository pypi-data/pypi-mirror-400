from __future__ import annotations

from excelminer.model.entities import (
    CellBlock,
    Connection,
    DefinedName,
    FormulaCell,
    PivotCache,
    PivotTable,
    PowerQuery,
    Sheet,
    Source,
)


def test_entities_factories_cover_optional_attrs_and_extra_merge() -> None:
    s_min = Source.make(source_type="unknown", key="k1", id="src:k1")
    assert "server" not in s_min.attrs

    s_full = Source.make(
        source_type="sqlserver",
        key="k2",
        id="src:k2",
        server="HOST",
        database="DB",
        value="v",
        provider="SQLOLEDB",
        extra={"x": 1},
    )
    assert s_full.attrs["server"] == "HOST"
    assert s_full.attrs["database"] == "DB"
    assert s_full.attrs["value"] == "v"
    assert s_full.attrs["provider"] == "SQLOLEDB"
    assert s_full.attrs["x"] == 1

    c1 = Connection.make(key="c", id="conn:c", name="N")
    assert "raw" not in c1.attrs

    c2 = Connection.make(key="c2", id="conn:c2", name="N2", raw="abc", details={"d": 2})
    assert c2.attrs["raw"] == "abc"
    assert c2.attrs["d"] == 2

    pq = PowerQuery.make(
        key="pq", id="pq:pq", name="Query", m_code="let x=1 in x", extra={"a": "b"}
    )
    assert pq.attrs["m_code"].startswith("let")
    assert pq.attrs["a"] == "b"

    pc = PivotCache.make(
        key="pc",
        id="pc:pc",
        cache_id="1",
        source_type="worksheet",
        source_ref="Sheet1!A1:B2",
        extra={"e": True},
    )
    assert pc.attrs["cache_id"] == "1"
    assert pc.attrs["source_type"] == "worksheet"
    assert pc.attrs["source_reference"] == "Sheet1!A1:B2"
    assert pc.attrs["e"] is True

    pt = PivotTable.make(
        key="pt",
        id="pt:pt",
        name="Pivot",
        sheet_name="Sheet1",
        measures=[{"name": "m"}],
        grouping_fields=[{"field": "f"}],
        extra={"x": 9},
    )
    assert pt.attrs["measures"][0]["name"] == "m"
    assert pt.attrs["grouping_fields"][0]["field"] == "f"
    assert pt.attrs["x"] == 9

    sh = Sheet.make(key="S", id="sheet:S", name="S", index=1, extra={"z": 0})
    assert sh.attrs["index"] == 1
    assert sh.attrs["z"] == 0

    dn = DefinedName.make(
        key="workbook|n",
        id="defined:workbook|n",
        name="n",
        scope="workbook",
        refers_to="Sheet1!A1",
        extra={"k": "v"},
    )
    assert dn.attrs["refers_to"] == "Sheet1!A1"
    assert dn.attrs["k"] == "v"

    cb = CellBlock.make(
        key="cb",
        id="block:cb",
        sheet_name="S",
        a1_range="A1:B2",
        block_type="table",
        stats={"rows": 2},
        sample=[[1, 2]],
        extra={"t": "x"},
    )
    assert cb.attrs["stats"]["rows"] == 2
    assert cb.attrs["sample"][0][0] == 1
    assert cb.attrs["t"] == "x"

    fc = FormulaCell.make(
        key="S!A1",
        id="formula:S!A1",
        sheet_name="S",
        address="A1",
        formula="=1+1",
        deps={"refs": []},
        extra={"u": 1},
    )
    assert fc.attrs["deps"] == {"refs": []}
    assert fc.attrs["u"] == 1
