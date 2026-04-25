"""Tests for gsrs_names."""
import pandas as pd
import pytest
from conftest import ASPIRIN_UNII, BASE, NAMES_LIST

from pygsrs import gsrs_names


def test_names_returns_dataframe(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})/names",
        json=NAMES_LIST,
    )
    out = gsrs_names(ASPIRIN_UNII)
    assert isinstance(out, pd.DataFrame)
    assert len(out) == len(NAMES_LIST)


def test_names_expected_columns(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})/names",
        json=NAMES_LIST,
    )
    out = gsrs_names(ASPIRIN_UNII)
    for col in ("name", "type", "query"):
        assert col in out.columns


def test_names_contains_aspirin(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})/names",
        json=NAMES_LIST,
    )
    out = gsrs_names(ASPIRIN_UNII)
    assert any("ASPIRIN" in str(n).upper() for n in out["name"])


def test_names_query_column_set(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})/names",
        json=NAMES_LIST,
    )
    out = gsrs_names(ASPIRIN_UNII)
    assert (out["query"] == ASPIRIN_UNII).all()


def test_names_handles_envelope_response(httpx_mock):
    """API may wrap result in a {"content": [...]} envelope."""
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})/names",
        json={"content": NAMES_LIST},
    )
    out = gsrs_names(ASPIRIN_UNII)
    assert isinstance(out, pd.DataFrame)
    assert len(out) == len(NAMES_LIST)


def test_names_empty_unii_returns_none():
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_names("")
    assert out is None


def test_names_http_error_returns_none(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances(NOTAREAL)/names",
        status_code=404,
    )
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_names("NOTAREAL")
    assert out is None
