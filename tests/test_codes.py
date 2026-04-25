"""Tests for gsrs_codes."""
import pandas as pd
import pytest
from conftest import ASPIRIN_UNII, BASE, CODES_LIST

from pygsrs import gsrs_codes


def test_codes_returns_dataframe(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})/codes",
        json=CODES_LIST,
    )
    out = gsrs_codes(ASPIRIN_UNII)
    assert isinstance(out, pd.DataFrame)
    assert len(out) == len(CODES_LIST)


def test_codes_expected_columns(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})/codes",
        json=CODES_LIST,
    )
    out = gsrs_codes(ASPIRIN_UNII)
    for col in ("code_system", "code", "query"):
        assert col in out.columns


def test_codes_contains_cas(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})/codes",
        json=CODES_LIST,
    )
    out = gsrs_codes(ASPIRIN_UNII)
    systems = out["code_system"].str.upper().tolist()
    assert any("CAS" in s for s in systems)


def test_codes_query_column_set(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})/codes",
        json=CODES_LIST,
    )
    out = gsrs_codes(ASPIRIN_UNII)
    assert (out["query"] == ASPIRIN_UNII).all()


def test_codes_handles_envelope_response(httpx_mock):
    """API may wrap result in a {"content": [...]} envelope."""
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})/codes",
        json={"content": CODES_LIST},
    )
    out = gsrs_codes(ASPIRIN_UNII)
    assert isinstance(out, pd.DataFrame)
    assert len(out) == len(CODES_LIST)


def test_codes_empty_unii_returns_none():
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_codes("")
    assert out is None


def test_codes_http_error_returns_none(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances(NOTAREAL)/codes",
        status_code=404,
    )
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_codes("NOTAREAL")
    assert out is None
