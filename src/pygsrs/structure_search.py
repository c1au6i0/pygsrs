"""gsrs_structure_search — search GSRS by chemical structure (SMILES)."""

from __future__ import annotations

from typing import Literal

import pandas as pd

from ._base import gsrs_get, graceful
from ._utils import parse_substances_response, empty_substances_df

SearchType = Literal["sub", "sim", "exact", "flex"]


@graceful("GSRS structure search")
def gsrs_structure_search(
    smiles: str,
    type: SearchType = "sub",
    cutoff: float = 0.8,
    top: int = 10,
) -> pd.DataFrame | None:
    """
    Search GSRS for substances matching a chemical structure.

    Parameters
    ----------
    smiles:
        SMILES or SMARTS string (e.g. ``"CC(=O)Oc1ccccc1C(=O)O"``).
    type:
        Search type: ``"sub"`` (substructure), ``"sim"`` (similarity),
        ``"exact"`` (exact match), or ``"flex"`` (flexible/disconnected).
    cutoff:
        Tanimoto cutoff for similarity search (0–1). Default 0.8.
        Ignored for other types.
    top:
        Maximum number of records to return. Default 10.

    Returns
    -------
    pandas.DataFrame
        One row per matching substance plus a ``query_smiles`` column,
        or ``None`` on error.
    """
    if not isinstance(smiles, str) or not smiles.strip():
        raise ValueError("`smiles` must be a non-empty string.")
    if type not in ("sub", "sim", "exact", "flex"):
        raise ValueError("`type` must be one of 'sub', 'sim', 'exact', 'flex'.")

    params: dict = {"q": smiles, "type": type, "sync": "true", "top": int(top)}
    if type == "sim":
        params["cutoff"] = float(cutoff)

    data = gsrs_get("substances/structureSearch", params=params).json()

    out = parse_substances_response(data)
    if len(out) > top:
        out = out.iloc[:top].reset_index(drop=True)
    out["query_smiles"] = smiles
    return out
