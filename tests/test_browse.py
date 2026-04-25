"""Tests for gsrs_browse."""
import pandas as pd
import pytest
from conftest import BASE, SUBSTANCE_RECORD, SUBSTANCES_ENVELOPE

from pygsrs import gsrs_browse


def test_browse_returns_dataframe(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances?top=5&skip=0",
        json=SUBSTANCES_ENVELOPE,
    )
    out = gsrs_browse(top=5)
    assert isinstance(out, pd.DataFrame)
    assert len(out) > 0


def test_browse_expected_columns(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances?top=5&skip=0",
        json=SUBSTANCES_ENVELOPE,
    )
    out = gsrs_browse(top=5)
    for col in ("uuid", "approval_id", "preferred_name", "date_retrieved"):
        assert col in out.columns


def test_browse_respects_top(httpx_mock):
    big = {"content": [SUBSTANCE_RECORD] * 5}
    httpx_mock.add_response(
        url=f"{BASE}/substances?top=3&skip=0",
        json=big,
    )
    out = gsrs_browse(top=3)
    assert len(out) <= 3


def test_browse_skip_offset(httpx_mock):
    record_2 = {**SUBSTANCE_RECORD, "uuid": "other-uuid", "approvalID": "OTHERUNII1"}
    httpx_mock.add_response(
        url=f"{BASE}/substances?top=5&skip=5",
        json={"content": [record_2]},
    )
    out = gsrs_browse(top=5, skip=5)
    assert "other-uuid" in out["uuid"].values


@pytest.mark.httpx_mock(assert_all_requests_were_expected=False)
def test_browse_http_error_returns_none(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances?top=10&skip=0",
        status_code=503,
    )
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_browse()
    assert out is None
