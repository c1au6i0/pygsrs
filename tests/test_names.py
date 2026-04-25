import pytest
import pandas as pd
from pygsrs import gsrs_names

ASPIRIN_UNII = "R16CO5Y76E"


def test_names_returns_dataframe():
    out = gsrs_names(ASPIRIN_UNII)
    assert isinstance(out, pd.DataFrame)
    assert len(out) > 0


def test_names_expected_columns():
    out = gsrs_names(ASPIRIN_UNII)
    for col in ("name", "type", "query"):
        assert col in out.columns


def test_names_contains_aspirin():
    out = gsrs_names(ASPIRIN_UNII)
    assert any("ASPIRIN" in str(n).upper() for n in out["name"])


def test_names_query_column_set():
    out = gsrs_names(ASPIRIN_UNII)
    assert (out["query"] == ASPIRIN_UNII).all()


def test_names_invalid_unii_returns_none():
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_names("NOTAREALUNII00000")
    assert out is None
