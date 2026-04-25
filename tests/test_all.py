"""Tests for gsrs_all."""
import pandas as pd
import pytest
from conftest import (
    ASPIRIN_NAME,
    ASPIRIN_UNII,
    BASE,
    CODES_LIST,
    HIERARCHY_LIST,
    NAMES_LIST,
    SUBSTANCE_FULL,
    SUBSTANCES_ENVELOPE,
)

from pygsrs import gsrs_all


def _mock_all(httpx_mock):
    """Register mock responses for all five sub-endpoints."""
    httpx_mock.add_response(
        url=f"{BASE}/substances/search?q=root_approvalID%3A{ASPIRIN_UNII}&top=1",
        json=SUBSTANCES_ENVELOPE,
    )
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})/names",
        json=NAMES_LIST,
    )
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})/codes",
        json=CODES_LIST,
    )
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})",
        json=SUBSTANCE_FULL,
    )
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})/@hierarchy",
        json=HIERARCHY_LIST,
    )


def test_all_returns_dict(httpx_mock):
    _mock_all(httpx_mock)
    out = gsrs_all(ASPIRIN_UNII)
    assert isinstance(out, dict)


def test_all_has_correct_keys(httpx_mock):
    _mock_all(httpx_mock)
    out = gsrs_all(ASPIRIN_UNII)
    assert set(out.keys()) == {"substance", "names", "codes", "structure", "hierarchy"}


def test_all_substance_is_dataframe(httpx_mock):
    _mock_all(httpx_mock)
    out = gsrs_all(ASPIRIN_UNII)
    assert isinstance(out["substance"], pd.DataFrame)
    assert len(out["substance"]) > 0


def test_all_names_contains_aspirin(httpx_mock):
    _mock_all(httpx_mock)
    out = gsrs_all(ASPIRIN_UNII)
    assert any(ASPIRIN_NAME in str(n).upper() for n in out["names"]["name"])


def test_all_structure_has_formula(httpx_mock):
    _mock_all(httpx_mock)
    out = gsrs_all(ASPIRIN_UNII)
    assert out["structure"]["formula"].iloc[0] == "C9H8O4"


def test_all_invalid_unii_returns_none():
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_all("")
    assert out is None
