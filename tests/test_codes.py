import pytest
import pandas as pd
from pygsrs import gsrs_codes

ASPIRIN_UNII = "R16CO5Y76E"


def test_codes_returns_dataframe():
    out = gsrs_codes(ASPIRIN_UNII)
    assert isinstance(out, pd.DataFrame)
    assert len(out) > 0


def test_codes_expected_columns():
    out = gsrs_codes(ASPIRIN_UNII)
    for col in ("code_system", "code", "query"):
        assert col in out.columns


def test_codes_contains_cas():
    out = gsrs_codes(ASPIRIN_UNII)
    systems = out["code_system"].str.upper().tolist()
    assert any("CAS" in s for s in systems), "Expected CAS code for aspirin"


def test_codes_query_column_set():
    out = gsrs_codes(ASPIRIN_UNII)
    assert (out["query"] == ASPIRIN_UNII).all()


def test_codes_invalid_unii_returns_none():
    with pytest.warns(UserWarning, match="failed"):
        out = gsrs_codes("NOTAREALUNII00000")
    assert out is None
