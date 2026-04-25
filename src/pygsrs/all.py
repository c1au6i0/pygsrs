"""gsrs_all — retrieve all available data for a substance by UNII."""

from __future__ import annotations

import pandas as pd

from ._base import graceful
from .codes import gsrs_codes
from .hierarchy import gsrs_hierarchy
from .names import gsrs_names
from .structure import gsrs_structure
from .substance import gsrs_substance


@graceful("GSRS all-data lookup")
def gsrs_all(unii: str) -> dict[str, pd.DataFrame | None] | None:
    """
    Retrieve all available GSRS data for a substance in one call.

    Fetches substance metadata, names, codes, chemical structure,
    and relationship hierarchy by calling :func:`gsrs_substance`,
    :func:`gsrs_names`, :func:`gsrs_codes`, :func:`gsrs_structure`,
    and :func:`gsrs_hierarchy` internally.

    Parameters
    ----------
    unii:
        FDA UNII code (e.g. ``"R16CO5Y76E"``).

    Returns
    -------
    dict with keys:
        - ``"substance"`` — core substance record (from :func:`gsrs_substance`)
        - ``"names"`` — all registered names (from :func:`gsrs_names`)
        - ``"codes"`` — all external identifier codes (from :func:`gsrs_codes`)
        - ``"structure"`` — chemical structure data (from :func:`gsrs_structure`)
        - ``"hierarchy"`` — relationship hierarchy nodes (from :func:`gsrs_hierarchy`)

    Notes
    -----
    Individual values in the returned dict may be ``None`` if that data is
    unavailable — for example, ``"structure"`` will be an empty DataFrame
    for biological substances that have no defined chemical structure. Always
    null-check each key before use.

    Examples
    --------
    >>> data = gsrs_all("R16CO5Y76E")
    >>> data["substance"]["preferred_name"].iloc[0]
    'ASPIRIN'

    >>> data["names"]["name"].tolist()[:3]  # doctest: +SKIP
    ['ASPIRIN', 'Acetylsalicylic acid', ...]

    >>> if data["structure"] is not None and len(data["structure"]) > 0:
    ...     print(data["structure"]["smiles"].iloc[0])
    CC(=O)Oc1ccccc1C(=O)O
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
