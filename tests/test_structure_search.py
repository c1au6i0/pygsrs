"""Tests for gsrs_structure_search."""
import pandas as pd
import pytest
from conftest import ASPIRIN_SMILES, ASPIRIN_UNII, BASE, SUBSTANCES_ENVELOPE

from pygsrs import gsrs_structure_search


def test_structure_search_exact_returns_dataframe(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances/structureSearch?q={ASPIRIN_SMILES.replace('(', '%28').replace(')', '%29')}&type=exact&sync=true&top=10",
        json=SUBSTANCES_ENVELOPE,
    )
    out = gsrs_structure_search(ASPIRIN_SMILES, search_type="exact")
    assert isinstance(out, pd.DataFrame)
    assert len(out) > 0


def test_structure_search_exact_finds_aspirin(httpx_mock):
    httpx_mock.add_response(json=SUBSTANCES_ENVELOPE)
    out = gsrs_structure_search(ASPIRIN_SMILES, search_type="exact")
    assert ASPIRIN_UNII in out["approval_id"].values


def test_structure_search_query_smiles_column(httpx_mock):
    httpx_mock.add_response(json=SUBSTANCES_ENVELOPE)
    out = gsrs_structure_search(ASPIRIN_SMILES, search_type="exact")
    assert "query_smiles" in out.columns
    assert (out["query_smiles"] == ASPIRIN_SMILES).all()


def test_structure_search_respects_top(httpx_mock):
    big_envelope = {"content": SUBSTANCES_ENVELOPE["content"] * 5}
    httpx_mock.add_response(json=big_envelope)
    out = gsrs_structure_search(ASPIRIN_SMILES, search_type="sub", top=3)
    assert len(out) <= 3


def test_structure_search_invalid_type_returns_none():
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_structure_search(ASPIRIN_SMILES, search_type="notvalid")  # type: ignore[arg-type]
    assert out is None


def test_structure_search_empty_smiles_returns_none():
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_structure_search("")
    assert out is None


@pytest.mark.httpx_mock(assert_all_requests_were_expected=False)
def test_structure_search_http_error_returns_none(httpx_mock):
    httpx_mock.add_response(status_code=500)
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_structure_search(ASPIRIN_SMILES, search_type="exact")
    assert out is None
