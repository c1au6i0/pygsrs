import pytest
import pandas as pd
from pygsrs import gsrs_search

ASPIRIN_UNII = "R16CO5Y76E"


def test_search_returns_dataframe():
    out = gsrs_search("aspirin")
    assert isinstance(out, pd.DataFrame)
    assert len(out) > 0


def test_search_expected_columns():
    out = gsrs_search("aspirin")
    for col in ("uuid", "approval_id", "preferred_name", "substance_class",
                "status", "date_retrieved"):
        assert col in out.columns, f"Missing column: {col}"


def test_search_content_aspirin():
    out = gsrs_search("aspirin", top=10)
    assert ASPIRIN_UNII in out["approval_id"].values, (
        "UNII R16CO5Y76E (aspirin) not found in top-10 results"
    )


def test_search_respects_top():
    out = gsrs_search("aspirin", top=3)
    assert len(out) <= 3


def test_search_invalid_query_returns_none():
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_search("")
    assert out is None
