"""gsrs_search_all / gsrs_browse_all — auto-paginating helpers."""

from __future__ import annotations

import pandas as pd

from ._base import graceful, gsrs_get
from ._utils import empty_substances_df, parse_substances_response

_PAGE_SIZE = 100  # records per page for pagination


@graceful("GSRS search-all")
def gsrs_search_all(query: str) -> pd.DataFrame | None:
    """
    Search GSRS and automatically paginate through **all** results.

    Repeatedly calls the search endpoint with increasing ``skip`` values
    until no more records are returned.  For very broad queries this can
    return tens of thousands of rows, so consider using :func:`gsrs_search`
    with explicit ``top``/``skip`` parameters if you only need a subset.

    Parameters
    ----------
    query:
        Lucene query string (e.g. ``"aspirin"``).

    Returns
    -------
    pandas.DataFrame
        All matching substances in a single DataFrame, or ``None`` on error.

    Examples
    --------
    >>> df = gsrs_search_all("ibuprofen")
    >>> print(f"Total results: {len(df)}")
    """
    if not isinstance(query, str) or not query.strip():
        raise ValueError("`query` must be a non-empty string.")

    frames: list[pd.DataFrame] = []
    skip = 0

    while True:
        data = gsrs_get(
            "substances/search",
            params={"q": query, "top": _PAGE_SIZE, "skip": skip},
        ).json()
        page = parse_substances_response(data)
        if len(page) == 0:
            break
        frames.append(page)
        if len(page) < _PAGE_SIZE:
            break
        skip += _PAGE_SIZE

    if not frames:
        return empty_substances_df()
    return pd.concat(frames, ignore_index=True)


@graceful("GSRS browse-all")
def gsrs_browse_all() -> pd.DataFrame | None:
    """
    Browse all substances in GSRS by auto-paginating through the full list.

    Repeatedly calls the browse endpoint until no more records are returned.
    This may take several minutes and return hundreds of thousands of rows
    depending on the size of the GSRS database.

    Returns
    -------
    pandas.DataFrame
        All substances in a single DataFrame, or ``None`` on error.

    Examples
    --------
    >>> df = gsrs_browse_all()
    >>> print(f"Total substances: {len(df)}")
    """
    frames: list[pd.DataFrame] = []
    skip = 0

    while True:
        data = gsrs_get(
            "substances",
            params={"top": _PAGE_SIZE, "skip": skip},
        ).json()
        page = parse_substances_response(data)
        if len(page) == 0:
            break
        frames.append(page)
        if len(page) < _PAGE_SIZE:
            break
        skip += _PAGE_SIZE

    if not frames:
        return empty_substances_df()
    return pd.concat(frames, ignore_index=True)
