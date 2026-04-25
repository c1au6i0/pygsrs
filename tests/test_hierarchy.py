"""Tests for gsrs_hierarchy."""
import pandas as pd
import pytest
from conftest import ASPIRIN_UNII, BASE, HIERARCHY_LIST

from pygsrs import gsrs_hierarchy


def test_hierarchy_returns_dataframe(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})/@hierarchy",
        json=HIERARCHY_LIST,
    )
    out = gsrs_hierarchy(ASPIRIN_UNII)
    assert isinstance(out, pd.DataFrame)
    assert len(out) == len(HIERARCHY_LIST)


def test_hierarchy_expected_columns(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})/@hierarchy",
        json=HIERARCHY_LIST,
    )
    out = gsrs_hierarchy(ASPIRIN_UNII)
    for col in ("text", "type", "depth", "query"):
        assert col in out.columns


def test_hierarchy_query_column_set(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})/@hierarchy",
        json=HIERARCHY_LIST,
    )
    out = gsrs_hierarchy(ASPIRIN_UNII)
    assert (out["query"] == ASPIRIN_UNII).all()


def test_hierarchy_handles_envelope_response(httpx_mock):
    """API may wrap result in a {"content": [...]} envelope."""
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})/@hierarchy",
        json={"content": HIERARCHY_LIST},
    )
    out = gsrs_hierarchy(ASPIRIN_UNII)
    assert isinstance(out, pd.DataFrame)
    assert len(out) == len(HIERARCHY_LIST)


def test_hierarchy_empty_returns_empty_df(httpx_mock):
    """Substances with no hierarchy nodes return an empty DataFrame."""
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})/@hierarchy",
        json=[],
    )
    out = gsrs_hierarchy(ASPIRIN_UNII)
    assert isinstance(out, pd.DataFrame)
    assert len(out) == 0


def test_hierarchy_empty_unii_returns_none():
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_hierarchy("")
    assert out is None


def test_hierarchy_http_error_returns_none(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances(NOTAREAL)/@hierarchy",
        status_code=404,
    )
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_hierarchy("NOTAREAL")
    assert out is None
