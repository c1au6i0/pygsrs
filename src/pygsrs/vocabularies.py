"""gsrs_vocabularies — retrieve all GSRS controlled vocabulary terms."""

from __future__ import annotations

import pandas as pd

from ._base import gsrs_get, graceful
from ._utils import parse_vocabularies_response, empty_vocabularies_df


@graceful("GSRS vocabularies lookup")
def gsrs_vocabularies() -> pd.DataFrame | None:
    """
    Retrieve all controlled vocabulary domains and their terms from GSRS.

    Returns
    -------
    pandas.DataFrame
        One row per term across all vocabulary domains,
        or ``None`` on error.
    """
    data = gsrs_get("vocabularies").json()
    # API returns either a list directly or {"content": [...]}
    if isinstance(data, dict):
        data = data.get("content", [])
    return parse_vocabularies_response(data)
