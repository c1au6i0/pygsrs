"""gsrs_codes — retrieve all external codes for a substance by UNII."""

from __future__ import annotations

import pandas as pd

from ._base import gsrs_get, graceful
from ._utils import parse_codes_response, empty_codes_df


@graceful("GSRS codes lookup")
def gsrs_codes(unii: str) -> pd.DataFrame | None:
    """
    Retrieve all external identifier codes registered for a substance.

    Parameters
    ----------
    unii:
        FDA UNII code (e.g. ``"R16CO5Y76E"``).

    Returns
    -------
    pandas.DataFrame
        One row per code, or ``None`` on error.
    """
    if not isinstance(unii, str) or not unii.strip():
        raise ValueError("`unii` must be a non-empty string.")

    data = gsrs_get(f"substances({unii})/codes").json()
    return parse_codes_response(data, query=unii)
