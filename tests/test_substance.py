import pytest
import pandas as pd
from pygsrs import gsrs_substance

ASPIRIN_UNII = "R16CO5Y76E"


def test_substance_returns_dataframe():
    out = gsrs_substance(ASPIRIN_UNII)
    assert isinstance(out, pd.DataFrame)
    assert len(out) > 0


def test_substance_content_aspirin():
    out = gsrs_substance(ASPIRIN_UNII)
    assert ASPIRIN_UNII in out["approval_id"].values


def test_substance_invalid_returns_none():
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_substance("")
    assert out is None
