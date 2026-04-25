import pytest
import pandas as pd
from pygsrs import gsrs_unii_from_name

ASPIRIN_UNII = "R16CO5Y76E"


def test_unii_from_name_returns_dataframe():
    out = gsrs_unii_from_name("aspirin")
    assert isinstance(out, pd.DataFrame)
    assert len(out) > 0


def test_unii_from_name_finds_aspirin():
    out = gsrs_unii_from_name("aspirin")
    assert ASPIRIN_UNII in out["approval_id"].values, (
        "Expected UNII R16CO5Y76E for 'aspirin'"
    )


def test_unii_from_name_query_column():
    out = gsrs_unii_from_name("aspirin")
    assert (out["query_name"] == "aspirin").all()


def test_unii_from_name_nicotine():
    out = gsrs_unii_from_name("nicotine")
    assert any("nicotine" in str(n).lower() for n in out["preferred_name"])


def test_unii_from_name_invalid_returns_none():
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_unii_from_name("")
    assert out is None
