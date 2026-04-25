"""Tests for gsrs_search_all and gsrs_browse_all."""
import pandas as pd
import pytest
from conftest import BASE, SUBSTANCES_ENVELOPE

from pygsrs import gsrs_browse_all, gsrs_search_all


def test_search_all_single_page(httpx_mock):
    # Only one page returned (< PAGE_SIZE records), so loop stops
    httpx_mock.add_response(
        url=f"{BASE}/substances/search?q=aspirin&top=100&skip=0",
        json=SUBSTANCES_ENVELOPE,
    )
    out = gsrs_search_all("aspirin")
    assert isinstance(out, pd.DataFrame)
    assert len(out) == 1


def test_search_all_two_pages(httpx_mock):
    full_page = {"content": [SUBSTANCES_ENVELOPE["content"][0]] * 100}
    single_record = SUBSTANCES_ENVELOPE
    httpx_mock.add_response(
        url=f"{BASE}/substances/search?q=aspirin&top=100&skip=0",
        json=full_page,
    )
    httpx_mock.add_response(
        url=f"{BASE}/substances/search?q=aspirin&top=100&skip=100",
        json=single_record,
    )
    out = gsrs_search_all("aspirin")
    assert len(out) == 101


def test_search_all_empty_query_returns_none():
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_search_all("")
    assert out is None


def test_browse_all_single_page(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances?top=100&skip=0",
        json=SUBSTANCES_ENVELOPE,
    )
    out = gsrs_browse_all()
    assert isinstance(out, pd.DataFrame)
    assert len(out) == 1
