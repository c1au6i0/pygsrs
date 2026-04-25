"""gsrs_hierarchy — retrieve relationship hierarchy for a substance."""

from __future__ import annotations

import pandas as pd

from ._base import gsrs_get, graceful
from ._utils import parse_hierarchy_response, empty_hierarchy_df


@graceful("GSRS hierarchy lookup")
def gsrs_hierarchy(unii: str) -> pd.DataFrame | None:
    """
    Retrieve the parent/child relationship hierarchy for a substance.

    Parameters
    ----------
    unii:
        FDA UNII code (e.g. ``"R16CO5Y76E"``).

    Returns
    -------
    pandas.DataFrame
        One row per hierarchy node, or ``None`` on error.
    """
    if not isinstance(unii, str) or not unii.strip():
        raise ValueError("`unii` must be a non-empty string.")

    data = gsrs_get(f"substances({unii})/@hierarchy").json()
    return parse_hierarchy_response(data, query=unii)
