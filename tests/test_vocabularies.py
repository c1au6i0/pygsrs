"""Tests for gsrs_vocabularies."""
import pandas as pd
import pytest
from conftest import BASE, VOCABULARIES_LIST

from pygsrs import gsrs_vocabularies


def test_vocabularies_returns_dataframe(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/vocabularies",
        json=VOCABULARIES_LIST,
    )
    out = gsrs_vocabularies()
    assert isinstance(out, pd.DataFrame)
    assert len(out) > 0


def test_vocabularies_expected_columns(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/vocabularies",
        json=VOCABULARIES_LIST,
    )
    out = gsrs_vocabularies()
    for col in ("domain", "value", "display"):
        assert col in out.columns


def test_vocabularies_content(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/vocabularies",
        json=VOCABULARIES_LIST,
    )
    out = gsrs_vocabularies()
    assert "SUBSTANCE_CLASS" in out["domain"].values


def test_vocabularies_handles_envelope(httpx_mock):
    """API may return {"content": [...]} envelope."""
    httpx_mock.add_response(
        url=f"{BASE}/vocabularies",
        json={"content": VOCABULARIES_LIST},
    )
    out = gsrs_vocabularies()
    assert isinstance(out, pd.DataFrame)
    assert len(out) > 0


@pytest.mark.httpx_mock(assert_all_requests_were_expected=False)
def test_vocabularies_http_error_returns_none(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/vocabularies",
        status_code=500,
    )
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_vocabularies()
    assert out is None
