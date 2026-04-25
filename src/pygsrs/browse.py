"""gsrs_browse — paginated browse of all GSRS substances."""

from __future__ import annotations

import pandas as pd

from ._base import gsrs_get, graceful
from ._utils import parse_substances_response, empty_substances_df


@graceful("GSRS browse")
def gsrs_browse(top: int = 10, skip: int = 0) -> pd.DataFrame | None:
    """
    Browse all substances in GSRS (paginated).

    Parameters
    ----------
    top:
        Number of records to return. Default 10.
    skip:
        Number of records to skip. Default 0.

    Returns
    -------
    pandas.DataFrame
        One row per substance, or ``None`` on error.
    """
    data = gsrs_get(
        "substances",
        params={"top": int(top), "skip": int(skip)},
    ).json()

    out = parse_substances_response(data)
    if len(out) > top:
        out = out.iloc[:top].reset_index(drop=True)
    return out
