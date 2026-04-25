import pytest
import pandas as pd
from pygsrs import gsrs_hierarchy

ASPIRIN_UNII = "R16CO5Y76E"


def test_hierarchy_returns_dataframe():
    out = gsrs_hierarchy(ASPIRIN_UNII)
    assert isinstance(out, pd.DataFrame)


def test_hierarchy_expected_columns():
    out = gsrs_hierarchy(ASPIRIN_UNII)
    for col in ("text", "type", "depth", "query"):
        assert col in out.columns


def test_hierarchy_query_column_set():
    out = gsrs_hierarchy(ASPIRIN_UNII)
    if len(out) > 0:
        assert (out["query"] == ASPIRIN_UNII).all()


def test_hierarchy_invalid_returns_none():
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_hierarchy("NOTAREALUNII00000")
    assert out is None
