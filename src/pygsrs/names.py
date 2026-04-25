"""gsrs_names — retrieve all names for a substance by UNII."""

from __future__ import annotations

import pandas as pd

from ._base import graceful, gsrs_get
from ._utils import parse_names_response


@graceful("GSRS names lookup")
def gsrs_names(unii: str) -> pd.DataFrame | None:
    """
    Retrieve all names registered for a substance.

    Names include INN, USAN, trade names, synonyms, and other
    name types across languages.

    Parameters
    ----------
    unii:
        FDA UNII code (e.g. ``"R16CO5Y76E"``).

    Returns
    -------
    pandas.DataFrame
        One row per name, or ``None`` on error.
        Columns: ``name``, ``type``, ``language``, ``preferred``,
        ``display_name``, ``query``, ``date_retrieved``.

    Examples
    --------
    >>> names = gsrs_names("R16CO5Y76E")
    >>> "ASPIRIN" in names["name"].values
    True

    Filter to preferred names only:

    >>> preferred = names[names["preferred"] == True]
    """
    if not isinstance(unii, str) or not unii.strip():
        raise ValueError("`unii` must be a non-empty string.")

    data = gsrs_get(f"substances({unii})/names").json()
    # API may return a plain list or a {"content": [...]} envelope
    if isinstance(data, dict):
        data = data.get("content", [])
    return parse_names_response(data, query=unii)
