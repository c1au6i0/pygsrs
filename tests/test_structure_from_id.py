"""Tests for gsrs_structure_from_id."""
from __future__ import annotations

import urllib.parse

import pandas as pd
import pytest
from conftest import (
    ASPIRIN_SMILES,
    ASPIRIN_UNII,
    BASE,
    SUBSTANCE_FULL,
    SUBSTANCES_ENVELOPE,
)

from pygsrs import gsrs_structure_from_id

ASPIRIN_INCHIKEY = "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"
ASPIRIN_CAS = "50-78-2"
ASPIRIN_NAME = "ASPIRIN"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

STRUCTURE_URL = f"{BASE}/substances({ASPIRIN_UNII})"
SEARCH_URL = f"{BASE}/substances/search"
STRUCTURE_SEARCH_URL = f"{BASE}/substances/structureSearch"


def _structure_search_url(smiles: str) -> str:
    """Build the exact URL the structure search endpoint would receive."""
    params = urllib.parse.urlencode(
        {"q": smiles, "type": "exact", "sync": "true", "top": 1}
    )
    return f"{STRUCTURE_SEARCH_URL}?{params}"


# ---------------------------------------------------------------------------
# Auto-detect: UNII
# ---------------------------------------------------------------------------


def test_from_id_unii_auto(httpx_mock):
    """10-char alphanumeric identifier is detected as UNII — no resolve step."""
    httpx_mock.add_response(url=STRUCTURE_URL, json=SUBSTANCE_FULL)
    out = gsrs_structure_from_id(ASPIRIN_UNII)
    assert isinstance(out, pd.DataFrame)
    assert out["smiles"].iloc[0] == ASPIRIN_SMILES


def test_from_id_unii_explicit(httpx_mock):
    """Explicit id_type='unii' skips detection and goes straight to structure."""
    httpx_mock.add_response(url=STRUCTURE_URL, json=SUBSTANCE_FULL)
    out = gsrs_structure_from_id(ASPIRIN_UNII, id_type="unii")
    assert isinstance(out, pd.DataFrame)
    assert len(out) == 1


# ---------------------------------------------------------------------------
# Auto-detect: name
# ---------------------------------------------------------------------------


def test_from_id_name_auto(httpx_mock):
    """Plain text falls through to name resolution."""
    httpx_mock.add_response(
        url=f"{SEARCH_URL}?q=root_names_name%3A%22{ASPIRIN_NAME}%22&top=1",
        json=SUBSTANCES_ENVELOPE,
    )
    httpx_mock.add_response(url=STRUCTURE_URL, json=SUBSTANCE_FULL)
    out = gsrs_structure_from_id(ASPIRIN_NAME)
    assert isinstance(out, pd.DataFrame)
    assert out["smiles"].iloc[0] == ASPIRIN_SMILES


def test_from_id_name_explicit(httpx_mock):
    """Explicit id_type='name' forces name resolution path."""
    httpx_mock.add_response(
        url=f"{SEARCH_URL}?q=root_names_name%3A%22{ASPIRIN_NAME}%22&top=1",
        json=SUBSTANCES_ENVELOPE,
    )
    httpx_mock.add_response(url=STRUCTURE_URL, json=SUBSTANCE_FULL)
    out = gsrs_structure_from_id(ASPIRIN_NAME, id_type="name")
    assert isinstance(out, pd.DataFrame)
    assert len(out) == 1


# ---------------------------------------------------------------------------
# Auto-detect: SMILES
# ---------------------------------------------------------------------------


def test_from_id_smiles_auto(httpx_mock):
    """String with structural tokens is detected as SMILES."""
    httpx_mock.add_response(
        url=_structure_search_url(ASPIRIN_SMILES),
        json=SUBSTANCES_ENVELOPE,
    )
    httpx_mock.add_response(url=STRUCTURE_URL, json=SUBSTANCE_FULL)
    out = gsrs_structure_from_id(ASPIRIN_SMILES)
    assert isinstance(out, pd.DataFrame)
    assert out["inchi_key"].iloc[0] == ASPIRIN_INCHIKEY


def test_from_id_smiles_explicit(httpx_mock):
    """Explicit id_type='smiles'."""
    httpx_mock.add_response(
        url=_structure_search_url(ASPIRIN_SMILES),
        json=SUBSTANCES_ENVELOPE,
    )
    httpx_mock.add_response(url=STRUCTURE_URL, json=SUBSTANCE_FULL)
    out = gsrs_structure_from_id(ASPIRIN_SMILES, id_type="smiles")
    assert isinstance(out, pd.DataFrame)
    assert len(out) == 1


# ---------------------------------------------------------------------------
# Auto-detect: InChIKey
# ---------------------------------------------------------------------------


def test_from_id_inchikey_auto(httpx_mock):
    """27-char InChIKey pattern is detected correctly."""
    httpx_mock.add_response(
        url=_structure_search_url(ASPIRIN_INCHIKEY),
        json=SUBSTANCES_ENVELOPE,
    )
    httpx_mock.add_response(url=STRUCTURE_URL, json=SUBSTANCE_FULL)
    out = gsrs_structure_from_id(ASPIRIN_INCHIKEY)
    assert isinstance(out, pd.DataFrame)
    assert out["formula"].iloc[0] == "C9H8O4"


def test_from_id_inchikey_explicit(httpx_mock):
    """Explicit id_type='inchikey'."""
    httpx_mock.add_response(
        url=_structure_search_url(ASPIRIN_INCHIKEY),
        json=SUBSTANCES_ENVELOPE,
    )
    httpx_mock.add_response(url=STRUCTURE_URL, json=SUBSTANCE_FULL)
    out = gsrs_structure_from_id(ASPIRIN_INCHIKEY, id_type="inchikey")
    assert isinstance(out, pd.DataFrame)
    assert len(out) == 1


# ---------------------------------------------------------------------------
# Auto-detect: CAS
# ---------------------------------------------------------------------------


def test_from_id_cas_auto(httpx_mock):
    """CAS pattern (e.g. 50-78-2) is detected and resolved via free-text search."""
    httpx_mock.add_response(
        url=f"{SEARCH_URL}?q={ASPIRIN_CAS}&top=1&skip=0",
        json=SUBSTANCES_ENVELOPE,
    )
    httpx_mock.add_response(url=STRUCTURE_URL, json=SUBSTANCE_FULL)
    out = gsrs_structure_from_id(ASPIRIN_CAS)
    assert isinstance(out, pd.DataFrame)
    assert out["smiles"].iloc[0] == ASPIRIN_SMILES


def test_from_id_cas_explicit(httpx_mock):
    """Explicit id_type='cas'."""
    httpx_mock.add_response(
        url=f"{SEARCH_URL}?q={ASPIRIN_CAS}&top=1&skip=0",
        json=SUBSTANCES_ENVELOPE,
    )
    httpx_mock.add_response(url=STRUCTURE_URL, json=SUBSTANCE_FULL)
    out = gsrs_structure_from_id(ASPIRIN_CAS, id_type="cas")
    assert isinstance(out, pd.DataFrame)
    assert len(out) == 1


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_from_id_empty_string_returns_none():
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_structure_from_id("")
    assert out is None


def test_from_id_name_no_match_returns_none(httpx_mock):
    """When name resolution returns empty results, function returns None."""
    httpx_mock.add_response(
        url=f"{SEARCH_URL}?q=root_names_name%3A%22NOTASUBSTANCE%22&top=1",
        json={"content": [], "total": 0, "count": 0, "skip": 0},
    )
    with pytest.warns(UserWarning, match="Could not resolve"):
        out = gsrs_structure_from_id("NOTASUBSTANCE")
    assert out is None


def test_from_id_smiles_no_match_returns_none(httpx_mock):
    """When structure search returns no hits, function returns None."""
    smiles = "C#N"
    httpx_mock.add_response(
        url=_structure_search_url(smiles),
        json={"content": [], "total": 0, "count": 0, "skip": 0},
    )
    with pytest.warns(UserWarning, match="Could not resolve"):
        out = gsrs_structure_from_id(smiles)
    assert out is None


def test_from_id_returns_correct_columns(httpx_mock):
    """Output contains all expected structure columns."""
    httpx_mock.add_response(url=STRUCTURE_URL, json=SUBSTANCE_FULL)
    out = gsrs_structure_from_id(ASPIRIN_UNII)
    for col in ("smiles", "formula", "mwt", "inchi_key", "query"):
        assert col in out.columns
