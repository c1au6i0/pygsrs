import pytest
import pandas as pd
from pygsrs import gsrs_browse


def test_browse_returns_dataframe():
    out = gsrs_browse(top=5)
    assert isinstance(out, pd.DataFrame)
    assert len(out) > 0


def test_browse_expected_columns():
    out = gsrs_browse(top=5)
    for col in ("uuid", "approval_id", "preferred_name", "date_retrieved"):
        assert col in out.columns


def test_browse_respects_top():
    out = gsrs_browse(top=3)
    assert len(out) <= 3


def test_browse_skip_returns_different_results():
    out_a = gsrs_browse(top=5, skip=0)
    out_b = gsrs_browse(top=5, skip=5)
    # UUIDs should not fully overlap
    assert not set(out_a["uuid"]) == set(out_b["uuid"])
