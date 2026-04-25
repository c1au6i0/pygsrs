"""Tests for gsrs_substance."""
import pandas as pd
import pytest
from conftest import ASPIRIN_UNII, BASE, SUBSTANCES_ENVELOPE

from pygsrs import gsrs_substance


def test_substance_returns_dataframe(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances/search?q=root_approvalID%3A{ASPIRIN_UNII}&top=1",
        json=SUBSTANCES_ENVELOPE,
    )
    out = gsrs_substance(ASPIRIN_UNII)
    assert isinstance(out, pd.DataFrame)
    assert len(out) > 0


def test_substance_content_aspirin(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances/search?q=root_approvalID%3A{ASPIRIN_UNII}&top=1",
        json=SUBSTANCES_ENVELOPE,
    )
    out = gsrs_substance(ASPIRIN_UNII)
    assert ASPIRIN_UNII in out["approval_id"].values


def test_substance_has_query_column(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances/search?q=root_approvalID%3A{ASPIRIN_UNII}&top=1",
        json=SUBSTANCES_ENVELOPE,
    )
    out = gsrs_substance(ASPIRIN_UNII)
    assert "query" in out.columns
    assert (out["query"] == ASPIRIN_UNII).all()


def test_substance_empty_unii_returns_none():
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_substance("")
    assert out is None


def test_substance_http_error_returns_none(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances/search?q=root_approvalID%3ANOTAREAL&top=1",
        status_code=404,
    )
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_substance("NOTAREAL")
    assert out is None
