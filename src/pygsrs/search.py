"""gsrs_search — full-text search of GSRS substances."""

from __future__ import annotations

import pandas as pd

from ._base import gsrs_get, graceful
from ._utils import parse_substances_response, empty_substances_df


@graceful("GSRS search")
def gsrs_search(query: str, top: int = 10, skip: int = 0) -> pd.DataFrame | None:
    """
    Search GSRS substances by free-text query.

    Parameters
    ----------
    query:
        Lucene query string (e.g. ``"aspirin"`` or ``"_name:aspirin"``).
    top:
        Maximum number of records to return. Default 10.
    skip:
        Number of records to skip (for pagination). Default 0.

    Returns
    -------
    pandas.DataFrame
        One row per matching substance, or ``None`` on error.
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("`query` must be a non-empty string.")

    data = gsrs_get(
        "substances/search",
        params={"q": query, "top": int(top), "skip": int(skip)},
    ).json()

    out = parse_substances_response(data)
    if len(out) > top:
        out = out.iloc[:top].reset_index(drop=True)
    return out
