"""gsrs_browse — paginated browse of all GSRS substances."""

from __future__ import annotations

import pandas as pd

from ._base import graceful, gsrs_get
from ._utils import parse_substances_response


@graceful("GSRS browse")
def gsrs_browse(top: int = 10, skip: int = 0) -> pd.DataFrame | None:
    """
    Browse all substances in GSRS (paginated).

    Unlike :func:`gsrs_search`, this returns all substances without
    any query filter. Use ``top`` and ``skip`` to page through results.
    For fetching all substances automatically, use :func:`gsrs_browse_all`.

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
        Columns: ``uuid``, ``approval_id``, ``preferred_name``,
        ``substance_class``, ``status``, ``definition_type``,
        ``definition_level``, ``version``, ``names_url``, ``codes_url``,
        ``self_url``, ``date_retrieved``.

    Examples
    --------
    First page of 50 substances:

    >>> page = gsrs_browse(top=50, skip=0)

    Second page:

    >>> page2 = gsrs_browse(top=50, skip=50)
    """
    data = gsrs_get(
        "substances",
        params={"top": int(top), "skip": int(skip)},
    ).json()

    out = parse_substances_response(data)
    if len(out) > top:
        out = out.iloc[:top].reset_index(drop=True)
    return out
