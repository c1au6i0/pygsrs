"""gsrs_all — retrieve all available data for a substance by UNII."""

from __future__ import annotations

import pandas as pd

from ._base import graceful
from .substance import gsrs_substance
from .names import gsrs_names
from .codes import gsrs_codes
from .structure import gsrs_structure
from .hierarchy import gsrs_hierarchy


@graceful("GSRS all-data lookup")
def gsrs_all(unii: str) -> dict[str, pd.DataFrame | None] | None:
    """
    Retrieve all available GSRS data for a substance in one call.

    Fetches substance metadata, names, codes, chemical structure,
    and relationship hierarchy.

    Parameters
    ----------
    unii:
        FDA UNII code (e.g. ``"R16CO5Y76E"``).

    Returns
    -------
    dict with keys:
        - ``"substance"`` — core substance record
        - ``"names"`` — all registered names
        - ``"codes"`` — all external identifier codes
        - ``"structure"`` — chemical structure data
        - ``"hierarchy"`` — relationship hierarchy nodes
    """
    if not isinstance(unii, str) or not unii.strip():
        raise ValueError("`unii` must be a non-empty string.")

    return {
        "substance": gsrs_substance(unii),
        "names":     gsrs_names(unii),
        "codes":     gsrs_codes(unii),
        "structure": gsrs_structure(unii),
        "hierarchy": gsrs_hierarchy(unii),
    }
