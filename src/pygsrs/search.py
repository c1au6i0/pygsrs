"""gsrs_search — full-text search of GSRS substances."""

from __future__ import annotations

import pandas as pd

from ._base import graceful, gsrs_get
from ._utils import parse_substances_response


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
        Columns: ``uuid``, ``approval_id``, ``preferred_name``,
        ``substance_class``, ``status``, ``definition_type``,
        ``definition_level``, ``version``, ``names_url``, ``codes_url``,
        ``self_url``, ``date_retrieved``.

    Examples
    --------
    Simple keyword search:

    >>> df = gsrs_search("aspirin")
    >>> "R16CO5Y76E" in df["approval_id"].values
    True

    Lucene field syntax:

    >>> df = gsrs_search("_name:acetaminophen AND substanceClass:chemical")

    Paginated results:

    >>> page1 = gsrs_search("antibiotic", top=50, skip=0)
    >>> page2 = gsrs_search("antibiotic", top=50, skip=50)
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
