"""Tests for gsrs_structure."""
import pandas as pd
import pytest
from conftest import ASPIRIN_SMILES, ASPIRIN_UNII, BASE, SUBSTANCE_FULL

from pygsrs import gsrs_structure


def test_structure_returns_dataframe(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})",
        json=SUBSTANCE_FULL,
    )
    out = gsrs_structure(ASPIRIN_UNII)
    assert isinstance(out, pd.DataFrame)
    assert len(out) == 1


def test_structure_expected_columns(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})",
        json=SUBSTANCE_FULL,
    )
    out = gsrs_structure(ASPIRIN_UNII)
    for col in ("smiles", "formula", "mwt", "inchi_key", "query"):
        assert col in out.columns


def test_structure_smiles(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})",
        json=SUBSTANCE_FULL,
    )
    out = gsrs_structure(ASPIRIN_UNII)
    assert out["smiles"].iloc[0] == ASPIRIN_SMILES


def test_structure_formula(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})",
        json=SUBSTANCE_FULL,
    )
    out = gsrs_structure(ASPIRIN_UNII)
    assert out["formula"].iloc[0] == "C9H8O4"


def test_structure_inchi_key(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})",
        json=SUBSTANCE_FULL,
    )
    out = gsrs_structure(ASPIRIN_UNII)
    assert out["inchi_key"].iloc[0] == "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"


def test_structure_no_structure_returns_empty(httpx_mock):
    """Non-chemical substances have no structure key."""
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})",
        json={"uuid": "abc", "approvalID": ASPIRIN_UNII},
    )
    out = gsrs_structure(ASPIRIN_UNII)
    assert isinstance(out, pd.DataFrame)
    assert len(out) == 0


def test_structure_empty_unii_returns_none():
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_structure("")
    assert out is None


def test_structure_http_error_returns_none(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances(NOTAREAL)",
        status_code=404,
    )
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_structure("NOTAREAL")
    assert out is None
