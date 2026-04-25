import pytest
import pandas as pd
from pygsrs import gsrs_structure_search

ASPIRIN_SMILES = "CC(=O)Oc1ccccc1C(=O)O"
ASPIRIN_UNII = "R16CO5Y76E"


def test_structure_search_exact_returns_dataframe():
    out = gsrs_structure_search(ASPIRIN_SMILES, type="exact")
    assert isinstance(out, pd.DataFrame)
    assert len(out) > 0


def test_structure_search_exact_finds_aspirin():
    out = gsrs_structure_search(ASPIRIN_SMILES, type="exact")
    assert ASPIRIN_UNII in out["approval_id"].values


def test_structure_search_query_smiles_column():
    out = gsrs_structure_search(ASPIRIN_SMILES, type="exact")
    assert (out["query_smiles"] == ASPIRIN_SMILES).all()


def test_structure_search_similarity_includes_aspirin():
    out = gsrs_structure_search(ASPIRIN_SMILES, type="sim", cutoff=0.9, top=10)
    assert ASPIRIN_UNII in out["approval_id"].values


def test_structure_search_respects_top():
    out = gsrs_structure_search(ASPIRIN_SMILES, type="sub", top=3)
    assert len(out) <= 3


def test_structure_search_invalid_smiles_returns_none():
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_structure_search("")
    assert out is None
