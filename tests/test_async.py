"""Tests for async API functions."""
import asyncio

import pandas as pd
from conftest import ASPIRIN_UNII, BASE, NAMES_LIST, SUBSTANCES_ENVELOPE

from pygsrs import agsrs_names, agsrs_search, agsrs_substance


def test_agsrs_substance_returns_dataframe(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances/search?q=root_approvalID%3A{ASPIRIN_UNII}&top=1",
        json=SUBSTANCES_ENVELOPE,
    )
    out = asyncio.run(agsrs_substance(ASPIRIN_UNII))
    assert isinstance(out, pd.DataFrame)
    assert ASPIRIN_UNII in out["approval_id"].values


def test_agsrs_search_returns_dataframe(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances/search?q=aspirin&top=10&skip=0",
        json=SUBSTANCES_ENVELOPE,
    )
    out = asyncio.run(agsrs_search("aspirin"))
    assert isinstance(out, pd.DataFrame)
    assert len(out) > 0


def test_agsrs_names_returns_dataframe(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})/names",
        json=NAMES_LIST,
    )
    out = asyncio.run(agsrs_names(ASPIRIN_UNII))
    assert isinstance(out, pd.DataFrame)
    assert len(out) == len(NAMES_LIST)


def test_agsrs_substance_empty_unii_returns_none():
    out = asyncio.run(agsrs_substance(""))
    assert out is None
