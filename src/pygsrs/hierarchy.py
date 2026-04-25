"""gsrs_hierarchy — retrieve relationship hierarchy for a substance."""

from __future__ import annotations

import pandas as pd

from ._base import graceful, gsrs_get
from ._utils import parse_hierarchy_response


@graceful("GSRS hierarchy lookup")
def gsrs_hierarchy(unii: str) -> pd.DataFrame | None:
    """
    Retrieve the parent/child relationship hierarchy for a substance.

    The hierarchy represents how substances relate to each other
    (e.g. a salt to its parent acid/base, a mixture to its components).

    Parameters
    ----------
    unii:
        FDA UNII code (e.g. ``"R16CO5Y76E"``).

    Returns
    -------
    pandas.DataFrame
        One row per hierarchy node, or ``None`` on error.
        Columns: ``text``, ``type``, ``depth``, ``expandable``,
        ``node_id``, ``parent``, ``approval_id``, ``name``,
        ``refuuid``, ``substance_class``, ``deprecated``,
        ``query``, ``date_retrieved``.

    Examples
    --------
    >>> tree = gsrs_hierarchy("R16CO5Y76E")
    >>> tree[["text", "type", "depth"]]
    """
    if not isinstance(unii, str) or not unii.strip():
        raise ValueError("`unii` must be a non-empty string.")

    data = gsrs_get(f"substances({unii})/@hierarchy").json()
    # API may return a plain list or a {"content": [...]} envelope
    if isinstance(data, dict):
        data = data.get("content", [])
    return parse_hierarchy_response(data, query=unii)
