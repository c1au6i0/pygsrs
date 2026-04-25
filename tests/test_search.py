"""Tests for gsrs_search."""
import pandas as pd
import pytest
from conftest import ASPIRIN_UNII, BASE, SUBSTANCES_ENVELOPE

from pygsrs import gsrs_search


def test_search_returns_dataframe(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances/search?q=aspirin&top=10&skip=0",
        json=SUBSTANCES_ENVELOPE,
    )
    out = gsrs_search("aspirin")
    assert isinstance(out, pd.DataFrame)
    assert len(out) == 1


def test_search_expected_columns(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances/search?q=aspirin&top=10&skip=0",
        json=SUBSTANCES_ENVELOPE,
    )
    out = gsrs_search("aspirin")
    for col in ("uuid", "approval_id", "preferred_name", "substance_class",
                "status", "date_retrieved"):
        assert col in out.columns, f"Missing column: {col}"


def test_search_content_aspirin(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances/search?q=aspirin&top=10&skip=0",
        json=SUBSTANCES_ENVELOPE,
    )
    out = gsrs_search("aspirin", top=10)
    assert ASPIRIN_UNII in out["approval_id"].values


def test_search_respects_top(httpx_mock):
    # Return 5 records but request top=3 — the function should truncate
    envelope = {"content": [SUBSTANCES_ENVELOPE["content"][0]] * 5}
    httpx_mock.add_response(
        url=f"{BASE}/substances/search?q=aspirin&top=3&skip=0",
        json=envelope,
    )
    out = gsrs_search("aspirin", top=3)
    assert len(out) <= 3


def test_search_empty_query_returns_none():
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_search("")
    assert out is None


def test_search_http_error_returns_none(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances/search?q=badquery&top=10&skip=0",
        status_code=404,
    )
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_search("badquery")
    assert out is None
