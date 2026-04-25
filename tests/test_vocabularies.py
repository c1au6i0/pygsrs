import pytest
import pandas as pd
from pygsrs import gsrs_vocabularies


def test_vocabularies_returns_dataframe():
    out = gsrs_vocabularies()
    assert isinstance(out, pd.DataFrame)
    assert len(out) > 0


def test_vocabularies_expected_columns():
    out = gsrs_vocabularies()
    for col in ("domain", "value", "display"):
        assert col in out.columns


def test_vocabularies_has_multiple_domains():
    out = gsrs_vocabularies()
    assert out["domain"].nunique() > 5
