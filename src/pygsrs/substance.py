"""gsrs_substance — look up a substance by UNII / approval ID."""

from __future__ import annotations

import pandas as pd

from ._base import gsrs_get, graceful
from ._utils import parse_substances_response, empty_substances_df


@graceful("GSRS substance lookup")
def gsrs_substance(unii: str) -> pd.DataFrame | None:
    """
    Retrieve a GSRS substance record by UNII (approval ID).

    Parameters
    ----------
    unii:
        FDA UNII code (e.g. ``"R16CO5Y76E"`` for aspirin).

    Returns
    -------
    pandas.DataFrame
        Single-row data frame, or ``None`` on error.
    """
    if not isinstance(unii, str) or not unii.strip():
        raise ValueError("`unii` must be a non-empty string.")

    data = gsrs_get(
        "substances/search",
        params={"q": f"root_approvalID:{unii}", "top": 1},
    ).json()

    out = parse_substances_response(data)
    out["query"] = unii
    return out
