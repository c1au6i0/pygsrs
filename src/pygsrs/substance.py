"""gsrs_substance — look up a substance by UNII / approval ID."""

from __future__ import annotations

import pandas as pd

from ._base import graceful, gsrs_get
from ._utils import parse_substances_response


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
        Single-row data frame with substance metadata plus a ``query``
        column, or ``None`` on error.
        Columns: ``uuid``, ``approval_id``, ``preferred_name``,
        ``substance_class``, ``status``, ``definition_type``,
        ``definition_level``, ``version``, ``names_url``, ``codes_url``,
        ``self_url``, ``date_retrieved``, ``query``.

    Examples
    --------
    >>> df = gsrs_substance("R16CO5Y76E")
    >>> df["preferred_name"].iloc[0]
    'ASPIRIN'

    >>> df["approval_id"].iloc[0]
    'R16CO5Y76E'
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
