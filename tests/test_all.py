import pytest
import pandas as pd
from pygsrs import gsrs_all

ASPIRIN_UNII = "R16CO5Y76E"


def test_all_returns_dict():
    out = gsrs_all(ASPIRIN_UNII)
    assert isinstance(out, dict)


def test_all_has_correct_keys():
    out = gsrs_all(ASPIRIN_UNII)
    assert set(out.keys()) == {"substance", "names", "codes", "structure", "hierarchy"}


def test_all_substance_is_dataframe():
    out = gsrs_all(ASPIRIN_UNII)
    assert isinstance(out["substance"], pd.DataFrame)
    assert len(out["substance"]) > 0


def test_all_names_contains_aspirin():
    out = gsrs_all(ASPIRIN_UNII)
    assert any("ASPIRIN" in str(n).upper() for n in out["names"]["name"])


def test_all_structure_has_formula():
    out = gsrs_all(ASPIRIN_UNII)
    assert out["structure"]["formula"].iloc[0] == "C9H8O4"


def test_all_invalid_returns_none():
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_all("")
    assert out is None
