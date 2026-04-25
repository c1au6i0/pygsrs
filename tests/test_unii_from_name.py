"""Tests for gsrs_unii_from_name."""
import pandas as pd
import pytest
from conftest import ASPIRIN_NAME, ASPIRIN_UNII, SUBSTANCES_ENVELOPE

from pygsrs import gsrs_unii_from_name


def test_unii_from_name_returns_dataframe(httpx_mock):
    httpx_mock.add_response(json=SUBSTANCES_ENVELOPE)
    out = gsrs_unii_from_name(ASPIRIN_NAME)
    assert isinstance(out, pd.DataFrame)
    assert len(out) > 0


def test_unii_from_name_finds_unii(httpx_mock):
    httpx_mock.add_response(json=SUBSTANCES_ENVELOPE)
    out = gsrs_unii_from_name(ASPIRIN_NAME)
    assert ASPIRIN_UNII in out["approval_id"].values


def test_unii_from_name_query_column(httpx_mock):
    httpx_mock.add_response(json=SUBSTANCES_ENVELOPE)
    out = gsrs_unii_from_name(ASPIRIN_NAME)
    assert "query_name" in out.columns
    assert (out["query_name"] == ASPIRIN_NAME).all()


def test_unii_from_name_empty_returns_none():
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_unii_from_name("")
    assert out is None


def test_unii_from_name_http_error_returns_none(httpx_mock):
    httpx_mock.add_response(status_code=404)
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_unii_from_name("NOTASUBSTANCE")
    assert out is None
