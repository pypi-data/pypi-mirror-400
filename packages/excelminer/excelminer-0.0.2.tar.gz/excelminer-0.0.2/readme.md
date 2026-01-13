# excelminer

`excelminer` extracts Excel workbook artifacts into a small, normalized in-memory graph (nodes + edges) that you can serialize to deterministic JSON.

It is designed for inventory, analysis, and reproducible diffs (stable ordering), not for “opening Excel” or evaluating formulas.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What you can extract

From OOXML files (`.xlsx/.xlsm/.xltx/.xltm`) without Excel installed:

- sheets
- defined names
- connections + basic source inference
- Power Query queries (when stored as `xl/queries/*.xml`)
- Power Query mashup-container detection (best-effort, metadata-only)
- pivot tables + pivot caches (best-effort)
- VBA project metadata + module text for macro-enabled OOXML (`.xlsm/.xltm/.xlam`)
- formula text + basic dependencies (via `openpyxl`, when enabled)

Optional enrichment:

- used-range “value blocks” via calamine (fast scanning)
- Windows Excel COM automation (for legacy formats like `.xls/.xlsb` and opt-in enrichment for modern OOXML)

This package focuses on *inventory and reproducible diffs*, not evaluation:

- formulas are stored as text (not evaluated)
- macros are not executed
- many artifacts are “best-effort” depending on how a workbook was authored

## Install

Base install:

```bash
pip install excelminer
```

Optional extras:

```bash
pip install "excelminer[calamine]"  # pandas + python-calamine
pip install "excelminer[com]"       # Windows + Microsoft Excel required
```

## Core API

- `analyze_workbook(path, *, options=..., backends=...) -> (graph, reports, ctx)`
- `analyze_to_dict(path, *, options=..., backends=...) -> dict`

`reports` is a per-backend list of stats/issues; `ctx.issues` includes top-level warnings.

## Quickstart

### JSON output

```python
from excelminer import AnalysisOptions, analyze_to_dict

result = analyze_to_dict(
    "workbook.xlsx",
    options=AnalysisOptions(include_formulas=True),
)

print(result["graph"]["stats"])          # counts by node kind
print(result["reports"][0]["backend"])    # per-backend reports
```

### Graph output

```python
from excelminer import AnalysisOptions, analyze_workbook

graph, reports, ctx = analyze_workbook(
    "workbook.xlsx",
    options=AnalysisOptions(include_formulas=True),
)

print(graph.stats())
print([r.backend for r in reports])
print(ctx.issues)
```

## Common usage patterns

### 1) Fast structural inventory (default)

```python
from excelminer import analyze_to_dict

result = analyze_to_dict("workbook.xlsx")
print(result["graph"]["stats"])  # counts by node kind
```

### 2) Formula inventory (no Excel required)

```python
from excelminer import AnalysisOptions, analyze_to_dict

result = analyze_to_dict(
    "workbook.xlsx",
    options=AnalysisOptions(include_formulas=True),
)
```

### 3) Used-range “value blocks” (optional)

Requires `excelminer[calamine]`.

```python
from excelminer import AnalysisOptions, analyze_to_dict

result = analyze_to_dict(
    "workbook.xlsx",
    options=AnalysisOptions(include_cells=True, max_cells_per_sheet=50_000),
)
```

### 4) Post-analysis distillation (optional)

If you want a condensed view for large graphs:

```python
from excelminer import AnalysisOptions, analyze_workbook

graph, reports, ctx = analyze_workbook(
    "workbook.xlsx",
    options=AnalysisOptions(include_formulas=True, post_analysis_distillation=True),
)
```

### 5) COM enrichment (Windows + Excel required)

COM is opt-in for modern OOXML files (`.xlsx/.xlsm/...`).

```python
from excelminer import AnalysisOptions, analyze_to_dict

result = analyze_to_dict(
    "workbook.xlsx",
    options=AnalysisOptions(include_com=True, include_connections=True),
)
```

## Output shape (high level)

`analyze_to_dict()` returns:

- `path`, `options`, `issues`
- `reports`: per-backend stats/issues
- `graph`: `{ nodes: [...], edges: [...], stats: {...} }`

Common node kinds include: `sheet`, `connection`, `source`, `powerquery`, `pivot_table`, `pivot_cache`, `vba_project`, `formula_cell`, `cell_block`.

Optional post-processing can be enabled via `AnalysisOptions(post_analysis_distillation=True)` to add condensed artifacts like `formula_group` and to prune unused artifacts (best-effort).

### Nodes and edges

- Node: `{ id, kind, key, attrs }`
- Edge: `{ src, dst, kind, attrs }`

Common edge kinds:

- `contains` (e.g. `sheet -> formula_cell`)
- `uses_source` (e.g. `connection -> source`)
- `uses_connection` (e.g. `powerquery -> connection`)
- `uses_cache` (e.g. `pivot_table -> pivot_cache`)
- `scoped_to` (e.g. `defined_name -> sheet`)

## Default backend pipeline

By default, backends run in this order:

1. OOXML zip parsing (structure)
2. VBA projects (macro detection for `.xlsm/.xltm/.xlam`)
3. Power Query (queries XML + mashup-container detection)
4. Pivot tables (pivots + caches)
5. Calamine (used-range/value blocks; optional)
6. openpyxl (formula text)
7. Excel COM (Windows-only enrichment; opt-in for modern OOXML)

You can override the pipeline via the `backends=` argument.

## Options (most important)

The main tuning surface is `excelminer.AnalysisOptions`.

Feature flags:

- `include_connections` (default `True`): workbook connections and inferred `source` nodes
- `include_powerquery` (default `True`): Power Query queries when stored as `xl/queries/*.xml`
- `include_pivots` (default `True`): pivot tables + caches (best-effort)
- `include_defined_names` (default `True`): defined names
- `include_vba` (default `True`): extract VBA project metadata and module text
- `include_formulas` (default `False`): formula text inventory via openpyxl
- `include_cells` (default `False`): used-range/value blocks via calamine (if installed)
- `include_com` (default `False`): enable Excel COM automation (Windows + Excel required)
- `post_analysis_distillation` (default `False`): optional graph distillation (best-effort)

Limits (for huge workbooks):

- `max_sheets`, `max_cells_per_sheet`
- `sample_rows_per_block`, `sample_cols_per_block` (calamine sampling)

## Data source discovery (connections / sources)

`excelminer` tries to normalize upstream data dependencies into `source` nodes.

Sources can be discovered via:

- OOXML connections (`xl/connections.xml`): OLEDB/ODBC connection strings (sanitized KV stored in `connection_kv`)
- OOXML external links (`xl/externalLinks/*`): external workbook/file links (best-effort)
- Power Query M scanning: regex-based inference of SQL/file/web/sharepoint sources
- COM connections (when enabled): additional connection metadata and file/web hints when available

If you suspect sources are missing, see the “QA helpers” below.

## QA helpers (recommended)

For quick inspection of whether sources and connections were detected:

```python
from excelminer import analyze_workbook, summarize_connections, summarize_sources

graph, reports, ctx = analyze_workbook("workbook.xlsx")

print(summarize_sources(graph)["counts"])
print(summarize_connections(graph)["counts"])
```

The connection summary also includes a `uses_source` mapping so you can see which connections did (or did not) map to sources.

## Security & privacy notes

- Connection parsing produces a sanitized key/value view (`password` / `user id` / etc masked) in `connection_kv`.
- The raw connection string may also be stored in `connection.raw`.

Treat the output JSON as potentially sensitive. If you don’t need connections, use `AnalysisOptions(include_connections=False)`.

Additional notes:

- Sanitization covers only a small set of common keys; connection strings and Power Query M can contain sensitive data in many forms.
- If you enable COM automation, Excel is started in the background; behavior can vary due to enterprise policies/add-ins.

## Troubleshooting

- If you see `openpyxl import failed`, install/upgrade `openpyxl`.
- If you enable `include_cells=True` and see a calamine/pandas error, install `excelminer[calamine]`.
- If you enable `include_com=True` and see `pywin32 not available`, install `excelminer[com]` (Windows only).
- Some Power Query workbooks store queries in binary mashup parts; `excelminer` reports presence/metadata but does not decode those binaries.

## Development notes

COM integration tests are opt-in because some environments can crash the Python process when Excel COM is invoked.

PowerShell:

```powershell
$env:EXCELMINER_RUN_COM_TESTS='1'
pytest -m integration
```
