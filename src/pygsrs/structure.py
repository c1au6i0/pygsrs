"""gsrs_structure — retrieve chemical structure data for a substance by UNII."""

from __future__ import annotations

import pandas as pd

from ._base import gsrs_get, graceful
from ._utils import parse_structure_response, empty_structure_df


@graceful("GSRS structure lookup")
def gsrs_structure(unii: str) -> pd.DataFrame | None:
    """
    Retrieve the chemical structure record for a substance.

    Parameters
    ----------
    unii:
        FDA UNII code (e.g. ``"R16CO5Y76E"``).

    Returns
    -------
    pandas.DataFrame
        Single-row data frame with SMILES, InChI, formula, etc.,
        or ``None`` on error.
    """
    if not isinstance(unii, str) or not unii.strip():
        raise ValueError("`unii` must be a non-empty string.")

    data = gsrs_get(f"substances({unii})").json()
    return parse_structure_response(data, query=unii)
