"""Async public API for pygsrs — async variants of all public functions."""

from __future__ import annotations

import pandas as pd

from ._async_base import graceful_async, gsrs_get_async
from ._utils import (
    parse_codes_response,
    parse_hierarchy_response,
    parse_names_response,
    parse_structure_response,
    parse_substances_response,
    parse_vocabularies_response,
)
from .structure_search import SearchType


@graceful_async("GSRS async search")
async def agsrs_search(
    query: str, top: int = 10, skip: int = 0
) -> pd.DataFrame | None:
    """Async variant of :func:`gsrs_search`."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("`query` must be a non-empty string.")
    data = (await gsrs_get_async(
        "substances/search",
        params={"q": query, "top": int(top), "skip": int(skip)},
    )).json()
    out = parse_substances_response(data)
    if len(out) > top:
        out = out.iloc[:top].reset_index(drop=True)
    return out


@graceful_async("GSRS async substance lookup")
async def agsrs_substance(unii: str) -> pd.DataFrame | None:
    """Async variant of :func:`gsrs_substance`."""
    if not isinstance(unii, str) or not unii.strip():
        raise ValueError("`unii` must be a non-empty string.")
    data = (await gsrs_get_async(
        "substances/search",
        params={"q": f"root_approvalID:{unii}", "top": 1},
    )).json()
    out = parse_substances_response(data)
    out["query"] = unii
    return out


@graceful_async("GSRS async names lookup")
async def agsrs_names(unii: str) -> pd.DataFrame | None:
    """Async variant of :func:`gsrs_names`."""
    if not isinstance(unii, str) or not unii.strip():
        raise ValueError("`unii` must be a non-empty string.")
    data = (await gsrs_get_async(f"substances({unii})/names")).json()
    if isinstance(data, dict):
        data = data.get("content", [])
    return parse_names_response(data, query=unii)


@graceful_async("GSRS async codes lookup")
async def agsrs_codes(unii: str) -> pd.DataFrame | None:
    """Async variant of :func:`gsrs_codes`."""
    if not isinstance(unii, str) or not unii.strip():
        raise ValueError("`unii` must be a non-empty string.")
    data = (await gsrs_get_async(f"substances({unii})/codes")).json()
    if isinstance(data, dict):
        data = data.get("content", [])
    return parse_codes_response(data, query=unii)


@graceful_async("GSRS async structure lookup")
async def agsrs_structure(unii: str) -> pd.DataFrame | None:
    """Async variant of :func:`gsrs_structure`."""
    if not isinstance(unii, str) or not unii.strip():
        raise ValueError("`unii` must be a non-empty string.")
    data = (await gsrs_get_async(f"substances({unii})")).json()
    return parse_structure_response(data, query=unii)


@graceful_async("GSRS async structure search")
async def agsrs_structure_search(
    smiles: str,
    search_type: SearchType = "sub",
    cutoff: float = 0.8,
    top: int = 10,
) -> pd.DataFrame | None:
    """Async variant of :func:`gsrs_structure_search`."""
    if not isinstance(smiles, str) or not smiles.strip():
        raise ValueError("`smiles` must be a non-empty string.")
    if search_type not in ("sub", "sim", "exact", "flex"):
        raise ValueError("`search_type` must be one of 'sub', 'sim', 'exact', 'flex'.")
    params: dict = {"q": smiles, "type": search_type, "sync": "true", "top": int(top)}
    if search_type == "sim":
        params["cutoff"] = float(cutoff)
    data = (await gsrs_get_async("substances/structureSearch", params=params)).json()
    out = parse_substances_response(data)
    if len(out) > top:
        out = out.iloc[:top].reset_index(drop=True)
    out["query_smiles"] = smiles
    return out


@graceful_async("GSRS async hierarchy lookup")
async def agsrs_hierarchy(unii: str) -> pd.DataFrame | None:
    """Async variant of :func:`gsrs_hierarchy`."""
    if not isinstance(unii, str) or not unii.strip():
        raise ValueError("`unii` must be a non-empty string.")
    data = (await gsrs_get_async(f"substances({unii})/@hierarchy")).json()
    if isinstance(data, dict):
        data = data.get("content", [])
    return parse_hierarchy_response(data, query=unii)


@graceful_async("GSRS async browse")
async def agsrs_browse(top: int = 10, skip: int = 0) -> pd.DataFrame | None:
    """Async variant of :func:`gsrs_browse`."""
    data = (await gsrs_get_async(
        "substances",
        params={"top": int(top), "skip": int(skip)},
    )).json()
    out = parse_substances_response(data)
    if len(out) > top:
        out = out.iloc[:top].reset_index(drop=True)
    return out


@graceful_async("GSRS async vocabularies lookup")
async def agsrs_vocabularies() -> pd.DataFrame | None:
    """Async variant of :func:`gsrs_vocabularies`."""
    data = (await gsrs_get_async("vocabularies")).json()
    if isinstance(data, dict):
        data = data.get("content", [])
    return parse_vocabularies_response(data)


@graceful_async("GSRS async UNII-from-name lookup")
async def agsrs_unii_from_name(name: str, top: int = 5) -> pd.DataFrame | None:
    """Async variant of :func:`gsrs_unii_from_name`."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("`name` must be a non-empty string.")
    data = (await gsrs_get_async(
        "substances/search",
        params={"q": f'root_names_name:"{name}"', "top": int(top)},
    )).json()
    out = parse_substances_response(data)
    if len(out) > top:
        out = out.iloc[:top].reset_index(drop=True)
    out["query_name"] = name
    return out


@graceful_async("GSRS async all-data lookup")
async def agsrs_all(unii: str) -> dict[str, pd.DataFrame | None] | None:
    """
    Async variant of :func:`gsrs_all`.

    Fetches all five sub-resources concurrently using :func:`asyncio.gather`.
    """
    import asyncio
    if not isinstance(unii, str) or not unii.strip():
        raise ValueError("`unii` must be a non-empty string.")
    substance, names, codes, structure, hierarchy = await asyncio.gather(
        agsrs_substance(unii),
        agsrs_names(unii),
        agsrs_codes(unii),
        agsrs_structure(unii),
        agsrs_hierarchy(unii),
    )
    return {
        "substance": substance,
        "names":     names,
        "codes":     codes,
        "structure": structure,
        "hierarchy": hierarchy,
    }
