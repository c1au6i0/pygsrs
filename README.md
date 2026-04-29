# pygsrs

**pygsrs** is a Python client library for the [FDA Global Substance Registration System (GSRS)](https://gsrs.ncats.nih.gov/) REST API. It provides a simple, Pythonic interface for querying the FDA's authoritative database of regulated substances — chemicals, biologics, proteins, nucleic acids, and more.

All public functions return [`pandas.DataFrame`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html) objects (or a `dict` of them for `gsrs_all`). On error, they return `None` and emit a `UserWarning` instead of raising exceptions, making them safe to use in data pipelines.

---

## What is GSRS?

The **Global Substance Registration System (GSRS)** is the FDA's authoritative database for identifying and registering substances. Every registered substance is assigned a **UNII** (Unique Ingredient Identifier) — a 10-character alphanumeric code (e.g. `R16CO5Y76E` for aspirin) that uniquely identifies a substance across regulatory systems worldwide.

---

## Installation

**With [uv](https://docs.astral.sh/uv/) (recommended):**

```bash
uv add pygsrs
```

**With [pixi](https://pixi.sh):**

```bash
pixi add --pypi pygsrs
```

Python 3.10+ is required.

### Optional dependencies

| Extra | Enables |
|---|---|
| `cache` | Disk-based HTTP caching via `diskcache` |

```bash
# uv
uv add "pygsrs[cache]"

# pixi
pixi add --pypi "pygsrs[cache]"
```

---

## Quick Start

```python
import pygsrs

# Free-text search
results = pygsrs.gsrs_search("aspirin")
print(results[["approval_id", "preferred_name", "substance_class"]])

# Look up a substance by UNII
aspirin = pygsrs.gsrs_substance("R16CO5Y76E")

# Get all names (INN, USAN, trade names, synonyms …)
names = pygsrs.gsrs_names("R16CO5Y76E")

# Get external codes (CAS, NCI, WHO, …)
codes = pygsrs.gsrs_codes("R16CO5Y76E")

# Get chemical structure — by UNII
structure = pygsrs.gsrs_structure("R16CO5Y76E")
print(structure[["smiles", "formula", "mwt", "inchi_key"]])

# Get chemical structure — from ANY identifier (auto-detected)
pygsrs.gsrs_structure_from_id("aspirin")                        # name
pygsrs.gsrs_structure_from_id("50-78-2")                        # CAS
pygsrs.gsrs_structure_from_id("BSYNRYMUTXBXSQ-UHFFFAOYSA-N")   # InChIKey
pygsrs.gsrs_structure_from_id("CC(=O)Oc1ccccc1C(=O)O")         # SMILES
pygsrs.gsrs_structure_from_id("R16CO5Y76E")                     # UNII

# Search by SMILES (substructure, similarity, exact, flex)
hits = pygsrs.gsrs_structure_search("CC(=O)Oc1ccccc1C(=O)O", search_type="exact")

# All data for a UNII in one call
data = pygsrs.gsrs_all("R16CO5Y76E")
print(data["names"])
print(data["structure"])
```

---

## Function Reference

### Summary

| Function | Description |
|---|---|
| [`gsrs_search`](#gsrs_searchquery-top10-skip0) | Free-text / Lucene search |
| [`gsrs_search_all`](#gsrs_search_allquery) | Auto-paginated free-text search |
| [`gsrs_substance`](#gsrs_substanceunii) | Look up a substance by UNII |
| [`gsrs_batch`](#gsrs_batchuniis-workers8) | Concurrent lookup for multiple UNIIs |
| [`gsrs_names`](#gsrs_namesunii) | All registered names for a substance |
| [`gsrs_codes`](#gsrs_codesunii) | All external codes (CAS, NCI, WHO, …) |
| [`gsrs_structure`](#gsrs_structureunii) | Chemical structure by UNII |
| [`gsrs_structure_from_id`](#gsrs_structure_from_ididentifier-id_typeauto) | Chemical structure from any identifier |
| [`gsrs_structure_search`](#gsrs_structure_searchsmiles-search_typesub-cutoff08-top10) | Structure search by SMILES |
| [`gsrs_hierarchy`](#gsrs_hierarchyunii) | Parent/child relationship hierarchy |
| [`gsrs_browse`](#gsrs_browsetop10-skip0) | Paginated browse of all substances |
| [`gsrs_browse_all`](#gsrs_browse_all) | Auto-paginated browse of all substances |
| [`gsrs_vocabularies`](#gsrs_vocabularies) | Controlled vocabulary terms |
| [`gsrs_unii_from_name`](#gsrs_unii_from_namename-top5) | Look up UNII by name |
| [`gsrs_all`](#gsrs_allunii) | All data for a substance in one call |

---

### `gsrs_search(query, top=10, skip=0)`

Full-text search using Lucene query syntax.

```python
# Simple keyword search
df = gsrs_search("ibuprofen")

# Lucene field search
df = gsrs_search("_name:acetaminophen AND substanceClass:chemical")

# Paginated results
page1 = gsrs_search("antibiotic", top=50, skip=0)
page2 = gsrs_search("antibiotic", top=50, skip=50)
```

**Returns:** `DataFrame` — columns: `uuid`, `approval_id`, `preferred_name`, `substance_class`, `status`, `definition_type`, `definition_level`, `version`, `names_url`, `codes_url`, `self_url`, `date_retrieved`.

---

### `gsrs_search_all(query)`

Auto-paginate through **all** search results for a query and return them in a single DataFrame.

```python
all_hits = gsrs_search_all("antibiotic")
print(f"Total results: {len(all_hits)}")
```

**Returns:** `DataFrame` — same columns as `gsrs_search`.

---

### `gsrs_substance(unii)`

Look up a single substance by its UNII code.

```python
df = gsrs_substance("R16CO5Y76E")       # Aspirin
print(df["preferred_name"].iloc[0])     # → 'ASPIRIN'
```

**Returns:** Single-row `DataFrame` — same columns as `gsrs_search` plus `query`.

---

### `gsrs_batch(uniis, workers=8)`

Fetch substance data for multiple UNIIs concurrently using a thread pool.

```python
uniis = ["R16CO5Y76E", "6M3C89ZY6R", "4G7DS2Q64Y"]   # aspirin, nicotine, caffeine
results = gsrs_batch(uniis)
print(results[["approval_id", "preferred_name"]])
```

**Returns:** `DataFrame` combining results from all UNIIs with a `query` column. Failed lookups are skipped with a warning.

---

### `gsrs_names(unii)`

Retrieve all registered names for a substance (INN, USAN, trade names, synonyms, etc.).

```python
names = gsrs_names("R16CO5Y76E")
print(names[["name", "type", "language", "preferred"]])
```

**Returns:** `DataFrame` — columns: `name`, `type`, `language`, `preferred`, `display_name`, `query`, `date_retrieved`.

---

### `gsrs_codes(unii)`

Retrieve all external identifier codes for a substance (CAS RN, NCI thesaurus code, WHO INN number, etc.).

```python
codes = gsrs_codes("R16CO5Y76E")
print(codes[["code_system", "code", "type"]])

# Find the CAS number
cas = codes.loc[codes["code_system"] == "CAS", "code"].iloc[0]  # → '50-78-2'
```

**Returns:** `DataFrame` — columns: `code_system`, `code`, `type`, `url`, `query`, `date_retrieved`.

---

### `gsrs_structure(unii)`

Retrieve the chemical structure record for a substance by UNII.

```python
struct = gsrs_structure("R16CO5Y76E")
print(struct[["smiles", "formula", "mwt", "inchi_key", "stereochemistry"]])
```

**Returns:** Single-row `DataFrame` — columns: `smiles`, `formula`, `mwt`, `inchi_key`, `inchi`, `stereochemistry`, `optical_activity`, `stereo_centers`, `defined_stereo`, `ez_centers`, `charge`, `molfile`, `query`, `date_retrieved`.

Returns an **empty** DataFrame for non-chemical substances (biologics, proteins, nucleic acids, etc.).

---

### `gsrs_structure_from_id(identifier, id_type="auto")`

Retrieve the chemical structure for a substance from **any common identifier**. The function resolves the identifier to a UNII first, then calls `gsrs_structure`.

| `id_type` | Identifier shape | Resolution |
|---|---|---|
| `"unii"` | 10-char alphanumeric — `"R16CO5Y76E"` | Direct structure lookup |
| `"name"` | Any name / INN / synonym — `"aspirin"` | `gsrs_unii_from_name` |
| `"smiles"` | SMILES string — `"CC(=O)Oc1ccccc1C(=O)O"` | `gsrs_structure_search` (exact) |
| `"inchikey"` | 27-char InChIKey — `"BSYNRYMUTXBXSQ-UHFFFAOYSA-N"` | `gsrs_structure_search` (exact) |
| `"cas"` | CAS Registry Number — `"50-78-2"` | `gsrs_search` (free-text) |
| `"auto"` | *(default)* | Inferred from string pattern |

Auto-detection rules (applied in order):

1. Matches `^[A-Z0-9]{10}$` → **UNII**
2. Matches `^[A-Z]{14}-[A-Z]{10}-[A-Z]$` → **InChIKey**
3. Matches `^\d{2,7}-\d{2}-\d$` → **CAS**
4. Contains `=`, `#`, `@`, `[`, `(`, etc. → **SMILES**
5. Anything else → **name**

```python
# Auto-detect (recommended)
gsrs_structure_from_id("R16CO5Y76E")                      # → UNII
gsrs_structure_from_id("aspirin")                          # → name
gsrs_structure_from_id("CC(=O)Oc1ccccc1C(=O)O")          # → SMILES
gsrs_structure_from_id("BSYNRYMUTXBXSQ-UHFFFAOYSA-N")    # → InChIKey
gsrs_structure_from_id("50-78-2")                         # → CAS

# Override when needed
gsrs_structure_from_id("50-78-2", id_type="cas")
gsrs_structure_from_id("aspirin",  id_type="name")
```

**Returns:** Same single-row `DataFrame` as `gsrs_structure`, or `None` if the identifier cannot be resolved or the substance has no defined structure.

---

### `gsrs_structure_search(smiles, search_type="sub", cutoff=0.8, top=10)`

Search GSRS by chemical structure using a SMILES string.

| `search_type` | Description |
|---|---|
| `"sub"` | Substructure — find substances containing the query |
| `"sim"` | Similarity — Tanimoto ≥ `cutoff` |
| `"exact"` | Exact structure match |
| `"flex"` | Flexible / disconnected fragment search |

```python
# Exact match
exact = gsrs_structure_search("CC(=O)Oc1ccccc1C(=O)O", search_type="exact")

# Similarity search (Tanimoto ≥ 0.9)
similar = gsrs_structure_search("CC(=O)Oc1ccccc1C(=O)O", search_type="sim", cutoff=0.9, top=20)

# Substructure search
subs = gsrs_structure_search("c1ccccc1", search_type="sub", top=50)
```

**Returns:** `DataFrame` — same columns as `gsrs_search` plus `query_smiles`.

---

### `gsrs_hierarchy(unii)`

Retrieve the parent/child relationship hierarchy for a substance.

```python
tree = gsrs_hierarchy("R16CO5Y76E")
print(tree[["text", "type", "depth", "approval_id"]])
```

**Returns:** `DataFrame` — columns: `text`, `type`, `depth`, `expandable`, `node_id`, `parent`, `approval_id`, `name`, `refuuid`, `substance_class`, `deprecated`, `query`, `date_retrieved`.

---

### `gsrs_browse(top=10, skip=0)`

Paginated browse of all substances in GSRS (no query filter).

```python
page = gsrs_browse(top=100, skip=0)
```

**Returns:** `DataFrame` — same columns as `gsrs_search`.

---

### `gsrs_browse_all()`

Auto-paginate through **all** substances in GSRS and return them in a single DataFrame. May take several minutes depending on network conditions.

```python
all_substances = gsrs_browse_all()
print(f"Total substances: {len(all_substances)}")
```

**Returns:** `DataFrame` — same columns as `gsrs_search`.

---

### `gsrs_vocabularies()`

Retrieve all controlled vocabulary domains and their terms. Useful for understanding valid values for fields like `substanceClass`, `name.type`, `code.codeSystem`, etc.

```python
vocab = gsrs_vocabularies()
print(vocab["domain"].unique())

# Filter to a specific domain
substance_classes = vocab.loc[vocab["domain"] == "SUBSTANCE_CLASS", "value"]
```

**Returns:** `DataFrame` — columns: `domain`, `term_type`, `value`, `display`, `hidden`, `selected`, `date_retrieved`.

---

### `gsrs_unii_from_name(name, top=5)`

Look up UNII codes by substance name using an exact phrase match on `root_names_name`.

```python
results = gsrs_unii_from_name("aspirin")
print(results[["approval_id", "preferred_name"]])
```

**Returns:** `DataFrame` — same columns as `gsrs_search` plus `query_name`.

---

### `gsrs_all(unii)`

Fetch all available data for a substance in one call. Internally calls `gsrs_substance`, `gsrs_names`, `gsrs_codes`, `gsrs_structure`, and `gsrs_hierarchy` concurrently.

```python
data = gsrs_all("R16CO5Y76E")

# data is a dict; each value is a DataFrame (or None for unavailable data)
print(data["substance"])
print(data["names"])
print(data["codes"])
print(data["structure"])
print(data["hierarchy"])
```

**Returns:** `dict[str, DataFrame | None]`. Individual keys may be `None` (e.g. no structure for a biologic).

---

## Async API

All public functions have async equivalents prefixed with `a`:

```python
import asyncio
import pygsrs

async def main():
    # Single async lookup
    df = await pygsrs.agsrs_substance("R16CO5Y76E")

    # Concurrent lookups
    uniis = ["R16CO5Y76E", "6M3C89ZY6R", "4G7DS2Q64Y"]
    results = await asyncio.gather(*[pygsrs.agsrs_substance(u) for u in uniis])

asyncio.run(main())
```

Available async functions:

| Async | Sync equivalent |
|---|---|
| `agsrs_search` | `gsrs_search` |
| `agsrs_substance` | `gsrs_substance` |
| `agsrs_names` | `gsrs_names` |
| `agsrs_codes` | `gsrs_codes` |
| `agsrs_structure` | `gsrs_structure` |
| `agsrs_structure_search` | `gsrs_structure_search` |
| `agsrs_hierarchy` | `gsrs_hierarchy` |
| `agsrs_browse` | `gsrs_browse` |
| `agsrs_vocabularies` | `gsrs_vocabularies` |
| `agsrs_unii_from_name` | `gsrs_unii_from_name` |
| `agsrs_all` | `gsrs_all` |

---

## CLI

pygsrs ships with a command-line interface for quick lookups from the terminal:

```bash
# Free-text search
pygsrs search aspirin
pygsrs search aspirin --top 20 --format csv

# Look up by UNII
pygsrs substance R16CO5Y76E

# Names, codes, hierarchy
pygsrs names R16CO5Y76E
pygsrs codes R16CO5Y76E
pygsrs hierarchy R16CO5Y76E

# Structure by UNII
pygsrs structure R16CO5Y76E

# Structure from any identifier (auto-detected)
pygsrs structure-from-id aspirin
pygsrs structure-from-id "50-78-2"
pygsrs structure-from-id "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
pygsrs structure-from-id "CC(=O)Oc1ccccc1C(=O)O"
pygsrs structure-from-id "50-78-2" --id-type cas      # explicit type

# Structure search by SMILES
pygsrs structure-search "CC(=O)Oc1ccccc1C(=O)O" --type exact
pygsrs structure-search "c1ccccc1" --type sub --top 50

# Browse all substances (paginated)
pygsrs browse --top 20 --skip 0

# Controlled vocabularies
pygsrs vocabularies

# Look up UNII by name
pygsrs unii-from-name aspirin

# All data for a UNII
pygsrs all R16CO5Y76E

# Output formats: table (default), csv, json
pygsrs names R16CO5Y76E --format json
pygsrs search ibuprofen --format csv
```

---

## Caching

Enable disk-based HTTP caching to avoid redundant API calls (requires the `cache` extra — see [Installation](#installation)):

```python
import pygsrs

# Enable caching (default location: ~/.cache/pygsrs)
pygsrs.enable_cache()

# Custom directory and TTL (seconds)
pygsrs.enable_cache(directory="/tmp/mygsrs", ttl=3600)

# Disable caching
pygsrs.disable_cache()

# Clear the cache
pygsrs.clear_cache()
```

---

## Error Handling

All functions use graceful error handling — on failure they return `None` and emit a `UserWarning` rather than raising an exception:

```python
import warnings
import pygsrs

# Check for None
result = pygsrs.gsrs_substance("NOT-A-REAL-UNII")
if result is None:
    print("Lookup failed")

# Capture the warning message
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    result = pygsrs.gsrs_substance("NOT-A-REAL-UNII")
    if result is None:
        print("Error:", w[-1].message)
```

---

## Configuration

```python
import pygsrs

# Point at a private GSRS deployment
pygsrs.set_base_url("https://my-gsrs-instance.example.com/api/v1")

# Reset to the public FDA instance
pygsrs.set_base_url()
```

---

## Development

```bash
# Clone and install in editable mode with dev deps
git clone https://github.com/heverz/pygsrs.git
cd pygsrs

# uv
uv sync --extra dev

# pixi
pixi install

# Run tests (fully offline — uses mocked HTTP via pytest-httpx)
pytest

# Linter
ruff check src/ tests/

# Type checker
mypy src/
```

---

## License

MIT
