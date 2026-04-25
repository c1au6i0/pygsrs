"""gsrs_codes — retrieve all external codes for a substance by UNII."""

from __future__ import annotations

import pandas as pd

from ._base import graceful, gsrs_get
from ._utils import parse_codes_response


@graceful("GSRS codes lookup")
def gsrs_codes(unii: str) -> pd.DataFrame | None:
    """
    Retrieve all external identifier codes registered for a substance.

    Codes include CAS Registry Numbers, NCI Thesaurus codes, WHO INN
    numbers, ChemSpider IDs, and many other external identifiers.

    Parameters
    ----------
    unii:
        FDA UNII code (e.g. ``"R16CO5Y76E"``).

    Returns
    -------
    pandas.DataFrame
        One row per code, or ``None`` on error.
        Columns: ``code_system``, ``code``, ``type``, ``url``,
        ``query``, ``date_retrieved``.

    Examples
    --------
    >>> codes = gsrs_codes("R16CO5Y76E")
    >>> print(codes[["code_system", "code"]].to_string())

    Filter to CAS numbers only:

    >>> cas = codes[codes["code_system"] == "CAS"]
    """
    if not isinstance(unii, str) or not unii.strip():
        raise ValueError("`unii` must be a non-empty string.")

    data = gsrs_get(f"substances({unii})/codes").json()
    # API may return a plain list or a {"content": [...]} envelope
    if isinstance(data, dict):
        data = data.get("content", [])
    return parse_codes_response(data, query=unii)
