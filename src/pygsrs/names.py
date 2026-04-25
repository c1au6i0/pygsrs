"""gsrs_names — retrieve all names for a substance by UNII."""

from __future__ import annotations

import pandas as pd

from ._base import gsrs_get, graceful
from ._utils import parse_names_response, empty_names_df


@graceful("GSRS names lookup")
def gsrs_names(unii: str) -> pd.DataFrame | None:
    """
    Retrieve all names registered for a substance.

    Parameters
    ----------
    unii:
        FDA UNII code (e.g. ``"R16CO5Y76E"``).

    Returns
    -------
    pandas.DataFrame
        One row per name, or ``None`` on error.
    """
    if not isinstance(unii, str) or not unii.strip():
        raise ValueError("`unii` must be a non-empty string.")

    data = gsrs_get(f"substances({unii})/names").json()
    return parse_names_response(data, query=unii)
