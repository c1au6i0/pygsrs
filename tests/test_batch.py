"""Tests for gsrs_batch."""
import pandas as pd
import pytest
from conftest import ASPIRIN_UNII, BASE, NICOTINE_UNII, SUBSTANCE_RECORD, SUBSTANCES_ENVELOPE

from pygsrs import gsrs_batch


def test_batch_returns_dataframe(httpx_mock):
    nicotine_record = {**SUBSTANCE_RECORD, "uuid": "nicotine-uuid", "approvalID": NICOTINE_UNII, "_name": "NICOTINE"}
    httpx_mock.add_response(
        url=f"{BASE}/substances/search?q=root_approvalID%3A{ASPIRIN_UNII}&top=1",
        json=SUBSTANCES_ENVELOPE,
    )
    httpx_mock.add_response(
        url=f"{BASE}/substances/search?q=root_approvalID%3A{NICOTINE_UNII}&top=1",
        json={"content": [nicotine_record]},
    )
    out = gsrs_batch([ASPIRIN_UNII, NICOTINE_UNII])
    assert isinstance(out, pd.DataFrame)
    assert len(out) == 2


def test_batch_approval_ids(httpx_mock):
    httpx_mock.add_response(
        url=f"{BASE}/substances/search?q=root_approvalID%3A{ASPIRIN_UNII}&top=1",
        json=SUBSTANCES_ENVELOPE,
    )
    out = gsrs_batch([ASPIRIN_UNII])
    assert ASPIRIN_UNII in out["approval_id"].values


def test_batch_empty_list_returns_none():
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_batch([])
    assert out is None
