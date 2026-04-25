"""gsrs_unii_from_name — look up the UNII for a substance by name."""

from __future__ import annotations

import pandas as pd

from ._base import gsrs_get, graceful
from ._utils import parse_substances_response, empty_substances_df


@graceful("GSRS UNII-from-name lookup")
def gsrs_unii_from_name(name: str, top: int = 5) -> pd.DataFrame | None:
    """
    Search GSRS for a substance by preferred name and return UNII codes.

    Parameters
    ----------
    name:
        Substance name to look up (e.g. ``"aspirin"``).
    top:
        Maximum number of candidate records to return. Default 5.

    Returns
    -------
    pandas.DataFrame
        Matching substances with ``approval_id`` (UNII) and
        ``preferred_name`` columns, or ``None`` on error.
    """
    if not isinstance(name, str) or not name.strip():
        raise ValueError("`name` must be a non-empty string.")

    data = gsrs_get(
        "substances/search",
        params={"q": f'root_names_name:"{name}"', "top": int(top)},
    ).json()

    out = parse_substances_response(data)
    if len(out) > top:
        out = out.iloc[:top].reset_index(drop=True)
    out["query_name"] = name
    return out
