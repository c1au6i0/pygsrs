import pytest
import pandas as pd
from pygsrs import gsrs_structure

ASPIRIN_UNII = "R16CO5Y76E"


def test_structure_returns_dataframe():
    out = gsrs_structure(ASPIRIN_UNII)
    assert isinstance(out, pd.DataFrame)
    assert len(out) == 1


def test_structure_expected_columns():
    out = gsrs_structure(ASPIRIN_UNII)
    for col in ("smiles", "formula", "mwt", "inchi_key", "query"):
        assert col in out.columns


def test_structure_aspirin_formula():
    out = gsrs_structure(ASPIRIN_UNII)
    assert out["formula"].iloc[0] == "C9H8O4", (
        f"Expected C9H8O4, got {out['formula'].iloc[0]}"
    )


def test_structure_aspirin_inchi_key():
    out = gsrs_structure(ASPIRIN_UNII)
    assert out["inchi_key"].iloc[0] == "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"


def test_structure_invalid_returns_none():
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_structure("NOTAREALUNII00000")
    assert out is None
