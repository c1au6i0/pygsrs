"""gsrs_structure — retrieve chemical structure data for a substance by UNII."""

from __future__ import annotations

import pandas as pd

from ._base import graceful, gsrs_get
from ._utils import parse_structure_response


@graceful("GSRS structure lookup")
def gsrs_structure(unii: str) -> pd.DataFrame | None:
    """
    Retrieve the chemical structure record for a substance.

    Returns an empty DataFrame for non-chemical substances such as
    biologics, proteins, or nucleic acids that do not have a defined
    small-molecule structure.

    Parameters
    ----------
    unii:
        FDA UNII code (e.g. ``"R16CO5Y76E"``).

    Returns
    -------
    pandas.DataFrame
        Single-row data frame with SMILES, InChI, formula, etc.,
        or ``None`` on error.
        Columns: ``smiles``, ``formula``, ``mwt``, ``inchi_key``,
        ``inchi``, ``stereochemistry``, ``optical_activity``,
        ``stereo_centers``, ``defined_stereo``, ``ez_centers``,
        ``charge``, ``molfile``, ``query``, ``date_retrieved``.

    Examples
    --------
    >>> struct = gsrs_structure("R16CO5Y76E")
    >>> struct["formula"].iloc[0]
    'C9H8O4'

    >>> struct["smiles"].iloc[0]
    'CC(=O)Oc1ccccc1C(=O)O'
    """
    if not isinstance(unii, str) or not unii.strip():
        raise ValueError("`unii` must be a non-empty string.")

    data = gsrs_get(f"substances({unii})").json()
    return parse_structure_response(data, query=unii)
