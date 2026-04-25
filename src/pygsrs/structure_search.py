"""gsrs_structure_search — search GSRS by chemical structure (SMILES)."""

from __future__ import annotations

from typing import Literal

import pandas as pd

from ._base import graceful, gsrs_get
from ._utils import parse_substances_response

SearchType = Literal["sub", "sim", "exact", "flex"]


@graceful("GSRS structure search")
def gsrs_structure_search(
    smiles: str,
    search_type: SearchType = "sub",
    cutoff: float = 0.8,
    top: int = 10,
) -> pd.DataFrame | None:
    """
    Search GSRS for substances matching a chemical structure.

    Parameters
    ----------
    smiles:
        SMILES or SMARTS string (e.g. ``"CC(=O)Oc1ccccc1C(=O)O"``).
    search_type:
        Search type: ``"sub"`` (substructure), ``"sim"`` (similarity),
        ``"exact"`` (exact match), or ``"flex"`` (flexible/disconnected).
        Default ``"sub"``.
    cutoff:
        Tanimoto cutoff for similarity search (0–1). Default 0.8.
        Ignored for other search types.
    top:
        Maximum number of records to return. Default 10.

    Returns
    -------
    pandas.DataFrame
        One row per matching substance plus a ``query_smiles`` column,
        or ``None`` on error.

    Examples
    --------
    Exact-match search for aspirin:

    >>> df = gsrs_structure_search("CC(=O)Oc1ccccc1C(=O)O", search_type="exact")
    >>> df["approval_id"].iloc[0]
    'R16CO5Y76E'

    Similarity search with a high Tanimoto cutoff:

    >>> df = gsrs_structure_search("CC(=O)Oc1ccccc1C(=O)O", search_type="sim", cutoff=0.95)
    """
    if not isinstance(smiles, str) or not smiles.strip():
        raise ValueError("`smiles` must be a non-empty string.")
    if search_type not in ("sub", "sim", "exact", "flex"):
        raise ValueError("`search_type` must be one of 'sub', 'sim', 'exact', 'flex'.")

    params: dict = {"q": smiles, "type": search_type, "sync": "true", "top": int(top)}
    if search_type == "sim":
        params["cutoff"] = float(cutoff)

    data = gsrs_get("substances/structureSearch", params=params).json()

    out = parse_substances_response(data)
    if len(out) > top:
        out = out.iloc[:top].reset_index(drop=True)
    out["query_smiles"] = smiles
    return out
