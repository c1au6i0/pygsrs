# pygsrs

**pygsrs** is a Python client library for the [FDA Global Substance Registration System (GSRS)](https://gsrs.ncats.nih.gov/) REST API. It provides a simple, Pythonic interface for querying the FDA's public database of regulated substances — chemicals, biologics, proteins, nucleic acids, and more.

All public functions return [`pandas.DataFrame`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html) objects (or a `dict` of them for `gsrs_all`). On error, they return `None` and emit a `UserWarning` instead of raising exceptions, making them safe for use in data pipelines.

---

## What is GSRS?

The **Global Substance Registration System (GSRS)** is the FDA's authoritative database for identifying and registering substances. Every registered substance is assigned a **UNII** (Unique Ingredient Identifier) — a 10-character alphanumeric code (e.g., `R16CO5Y76E` for aspirin) that uniquely identifies a substance across regulatory systems worldwide.

---

## Installation

```bash
pip install pygsrs
```

Python 3.10+ is required.

### Optional dependencies

| Feature | Install |
|---|---|
| Caching | `pip install pygsrs[cache]` |

---

## Quick Start

```python
import pygsrs

# Free-text search
results = pygsrs.gsrs_search("aspirin")
print(results[["approval_id", "preferred_name", "substance_class"]])

# Look up a substance by UNII
aspirin = pygsrs.gsrs_substance("R16CO5Y76E")

# Get all names for aspirin
names = pygsrs.gsrs_names("R16CO5Y76E")

# Get external codes (CAS, NCI, WHO, etc.)
codes = pygsrs.gsrs_codes("R16CO5Y76E")

# Get chemical structure info
structure = pygsrs.gsrs_structure("R16CO5Y76E")
print(structure[["smiles", "formula", "mwt", "inchi_key"]])

# Get structure from any identifier — UNII, name, SMILES, InChIKey, or CAS
structure = pygsrs.gsrs_structure_from_id("aspirin")           # by name
structure = pygsrs.gsrs_structure_from_id("50-78-2")           # by CAS
structure = pygsrs.gsrs_structure_from_id("BSYNRYMUTXBXSQ-UHFFFAOYSA-N")  # by InChIKey

# Search by SMILES (substructure, similarity, exact, flex)
hits = pygsrs.gsrs_structure_search("CC(=O)Oc1ccccc1C(=O)O", search_type="exact")

# All data for a UNII in one call
data = pygsrs.gsrs_all("R16CO5Y76E")
print(data["names"])
print(data["codes"])
```

---

## API Reference

### `gsrs_search(query, top=10, skip=0)`

Full-text search using Lucene query syntax.

```python
# Simple keyword search
df = gsrs_search("ibuprofen")

# Lucene field search
df = gsrs_search("_name:acetaminophen AND substanceClass:chemical")

# Pagination
page1 = gsrs_search("antibiotic", top=50, skip=0)
page2 = gsrs_search("antibiotic", top=50, skip=50)
```

**Returns:** `DataFrame` with columns: `uuid`, `approval_id`, `preferred_name`, `substance_class`, `status`, `definition_type`, `definition_level`, `version`, `names_url`, `codes_url`, `self_url`, `date_retrieved`.

---

### `gsrs_substance(unii)`

Look up a single substance by its UNII code.

```python
df = gsrs_substance("R16CO5Y76E")  # Aspirin
print(df["preferred_name"].iloc[0])  # → 'ASPIRIN'
```

**Returns:** Single-row `DataFrame` with the same columns as `gsrs_search`, plus a `query` column.

---

### `gsrs_names(unii)`

Retrieve all registered names for a substance (INN, USAN, trade names, synonyms, etc.).

```python
names = gsrs_names("R16CO5Y76E")
print(names[["name", "type", "language", "preferred"]])
```

**Returns:** `DataFrame` with columns: `name`, `type`, `language`, `preferred`, `display_name`, `query`, `date_retrieved`.

---

### `gsrs_codes(unii)`

Retrieve all external identifier codes for a substance (CAS RN, NCI thesaurus code, WHO INN number, etc.).

```python
codes = gsrs_codes("R16CO5Y76E")
print(codes[["code_system", "code", "type"]])
```

**Returns:** `DataFrame` with columns: `code_system`, `code`, `type`, `url`, `query`, `date_retrieved`.

---

### `gsrs_structure(unii)`

Retrieve the chemical structure record for a substance.

```python
struct = gsrs_structure("R16CO5Y76E")
print(struct[["smiles", "formula", "mwt", "inchi_key", "stereochemistry"]])
```

**Returns:** Single-row `DataFrame` with columns: `smiles`, `formula`, `mwt`, `inchi_key`, `inchi`, `stereochemistry`, `optical_activity`, `stereo_centers`, `defined_stereo`, `ez_centers`, `charge`, `molfile`, `query`, `date_retrieved`.

Returns an empty DataFrame for non-chemical substances (biologics, proteins, etc.).

---

### `gsrs_structure_from_id(identifier, id_type="auto")`

Retrieve the chemical structure for a substance identified by **any common identifier**.  The function resolves the identifier to a UNII first, then calls `gsrs_structure`.

| `id_type` | Identifier shape | Resolution strategy |
|---|---|---|
| `"unii"` | 10-char alphanumeric, e.g. `"R16CO5Y76E"` | Direct structure lookup |
| `"name"` | Any name / INN / synonym, e.g. `"aspirin"` | `gsrs_unii_from_name` |
| `"smiles"` | SMILES string, e.g. `"CC(=O)Oc1ccccc1C(=O)O"` | `gsrs_structure_search` (exact) |
| `"inchikey"` | 27-char InChIKey, e.g. `"BSYNRYMUTXBXSQ-UHFFFAOYSA-N"` | `gsrs_structure_search` (exact) |
| `"cas"` | CAS Registry Number, e.g. `"50-78-2"` | `gsrs_search` (free-text) |
| `"auto"` | *(default)* | Inferred from string pattern |

```python
# Auto-detect — pattern matching picks the right strategy
gsrs_structure_from_id("R16CO5Y76E")                      # UNII
gsrs_structure_from_id("aspirin")                          # name
gsrs_structure_from_id("CC(=O)Oc1ccccc1C(=O)O")          # SMILES
gsrs_structure_from_id("BSYNRYMUTXBXSQ-UHFFFAOYSA-N")    # InChIKey
gsrs_structure_from_id("50-78-2")                         # CAS

# Explicit id_type to override auto-detection
gsrs_structure_from_id("50-78-2", id_type="cas")
gsrs_structure_from_id("aspirin", id_type="name")
```

**Returns:** Same single-row `DataFrame` as `gsrs_structure`, or `None` if the identifier cannot be resolved or the substance has no structure.

---

### `gsrs_structure_search(smiles, search_type="sub", cutoff=0.8, top=10)`

Search GSRS by chemical structure using SMILES.

| `search_type` | Description |
|---|---|
| `"sub"` | Substructure search — find substances containing the query structure |
| `"sim"` | Similarity search — Tanimoto similarity ≥ `cutoff` |
| `"exact"` | Exact structure match |
| `"flex"` | Flexible/disconnected fragment search |

```python
# Exact match
exact = gsrs_structure_search("CC(=O)Oc1ccccc1C(=O)O", search_type="exact")

# Similarity search (Tanimoto ≥ 0.9)
similar = gsrs_structure_search("CC(=O)Oc1ccccc1C(=O)O", search_type="sim", cutoff=0.9, top=20)

# Substructure search
subs = gsrs_structure_search("c1ccccc1", search_type="sub", top=50)
```

**Returns:** `DataFrame` with the same columns as `gsrs_search` plus `query_smiles`.

---

### `gsrs_hierarchy(unii)`

Retrieve the parent/child relationship hierarchy for a substance.

```python
tree = gsrs_hierarchy("R16CO5Y76E")
print(tree[["text", "type", "depth", "approval_id"]])
```

**Returns:** `DataFrame` with columns: `text`, `type`, `depth`, `expandable`, `node_id`, `parent`, `approval_id`, `name`, `refuuid`, `substance_class`, `deprecated`, `query`, `date_retrieved`.

---

### `gsrs_browse(top=10, skip=0)`

Paginated browse of all substances in GSRS (no query filter).

```python
# First 100 substances
page = gsrs_browse(top=100, skip=0)
```

**Returns:** `DataFrame` with the same columns as `gsrs_search`.

---

### `gsrs_browse_all()`

Auto-paginate through **all** substances in GSRS and return them in a single DataFrame. This may take several minutes depending on network conditions.

```python
all_substances = gsrs_browse_all()
print(f"Total substances: {len(all_substances)}")
```

---

### `gsrs_vocabularies()`

Retrieve all controlled vocabulary domains and their terms. Useful for understanding valid values for fields like `substanceClass`, `name.type`, `code.codeSystem`, etc.

```python
vocab = gsrs_vocabularies()
domains = vocab["domain"].unique()
```

**Returns:** `DataFrame` with columns: `domain`, `term_type`, `value`, `display`, `hidden`, `selected`, `date_retrieved`.

---

### `gsrs_unii_from_name(name, top=5)`

Look up UNII codes by substance name.

```python
results = gsrs_unii_from_name("aspirin")
print(results[["approval_id", "preferred_name"]])
```

**Returns:** `DataFrame` with the same columns as `gsrs_search` plus `query_name`.

---

### `gsrs_all(unii)`

Fetch all available data for a substance in one call. Internally calls `gsrs_substance`, `gsrs_names`, `gsrs_codes`, `gsrs_structure`, and `gsrs_hierarchy`.

```python
data = gsrs_all("R16CO5Y76E")

# data is a dict; each key may be a DataFrame or None
print(data["substance"])
print(data["names"])
print(data["codes"])
print(data["structure"])
print(data["hierarchy"])
```

**Returns:** `dict[str, DataFrame | None]`. Individual keys may be `None` if that data is unavailable (e.g., no structure for a biologic).

---

### `gsrs_batch(uniis, workers=8)`

Fetch substance data for multiple UNIIs concurrently.

```python
uniis = ["R16CO5Y76E", "6M3C89ZY6R", "4G7DS2Q64Y"]  # aspirin, nicotine, caffeine
results = gsrs_batch(uniis)
print(results[["approval_id", "preferred_name"]])
```

**Returns:** `DataFrame` combining results from all UNIIs with a `query` column. Failed lookups are skipped with a warning.

---

### `gsrs_search_all(query)`

Auto-paginate through **all** search results for a query and return them in a single DataFrame.

```python
all_hits = gsrs_search_all("antibiotic")
print(f"Total results: {len(all_hits)}")
```

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
    tasks = [pygsrs.agsrs_substance(u) for u in uniis]
    results = await asyncio.gather(*tasks)

asyncio.run(main())
```

Available async functions: `agsrs_search`, `agsrs_substance`, `agsrs_names`, `agsrs_codes`, `agsrs_structure`, `agsrs_structure_search`, `agsrs_hierarchy`, `agsrs_browse`, `agsrs_vocabularies`, `agsrs_unii_from_name`, `agsrs_all`.

---

## CLI

pygsrs ships with a command-line interface for quick lookups:

```bash
# Search substances
pygsrs search aspirin

# Look up by UNII
pygsrs substance R16CO5Y76E

# Get names
pygsrs names R16CO5Y76E

# Get codes
pygsrs codes R16CO5Y76E

# Get structure
pygsrs structure R16CO5Y76E

# Structure search
pygsrs structure-search "CC(=O)Oc1ccccc1C(=O)O" --type exact

# Get all data
pygsrs all R16CO5Y76E

# Output as CSV
pygsrs search aspirin --format csv

# Output as JSON
pygsrs names R16CO5Y76E --format json
```

---

## Caching

Enable disk-based HTTP caching to avoid redundant API calls (requires `pip install pygsrs[cache]`):

```python
import pygsrs

# Enable caching (cache stored in ~/.cache/pygsrs by default)
pygsrs.enable_cache()

# Custom cache directory and TTL (seconds)
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

# Catch warnings programmatically
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    result = pygsrs.gsrs_substance("NOT-A-REAL-UNII")
    if result is None:
        print("Lookup failed:", w[-1].message)

# Or simply check for None
result = pygsrs.gsrs_names("R16CO5Y76E")
if result is not None:
    print(result)
```

---

## Configuration

```python
import pygsrs

# Use a different GSRS instance (e.g. a private deployment)
pygsrs.set_base_url("https://my-gsrs-instance.example.com/api/v1")

# Reset to the public FDA instance
pygsrs.set_base_url()
```

---

## Development

```bash
# Clone and install in editable mode with dev deps
git clone https://github.com/your-org/pygsrs.git
cd pygsrs
pip install -e ".[dev]"

# Run tests (offline, uses mocked HTTP)
pytest

# Run linter
ruff check src/ tests/

# Run type checker
mypy src/
```

---

## License

MIT
