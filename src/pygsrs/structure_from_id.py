"""gsrs_structure_from_id — resolve any identifier to a chemical structure."""

from __future__ import annotations

import re
import warnings
from typing import Literal

import pandas as pd

from ._base import graceful
from .search import gsrs_search
from .structure import gsrs_structure
from .structure_search import gsrs_structure_search
from .unii_from_name import gsrs_unii_from_name

# ---------------------------------------------------------------------------
# Patterns for auto-detection
# ---------------------------------------------------------------------------

# UNII: exactly 10 alphanumeric characters (uppercase letters + digits)
_UNII_RE = re.compile(r"^[A-Z0-9]{10}$")

# InChIKey: 27-char fixed format  XXXXXXXXXXXXXX-XXXXXXXXXX-X
_INCHIKEY_RE = re.compile(r"^[A-Z]{14}-[A-Z]{10}-[A-Z]$")

# CAS Registry Number: 2–7 digits, dash, 2 digits, dash, 1 digit
_CAS_RE = re.compile(r"^\d{2,7}-\d{2}-\d$")

# SMILES heuristic: contains at least one atom symbol and a structural token
# (bond, ring, branch, charge, etc.)
_SMILES_TOKENS = re.compile(r"[=#@+\-\[\]()\\/%]")

IdType = Literal["auto", "unii", "smiles", "inchikey", "cas", "name"]


def _detect(identifier: str) -> IdType:
    """Infer identifier type from string shape."""
    s = identifier.strip()
    if _UNII_RE.match(s):
        return "unii"
    if _INCHIKEY_RE.match(s):
        return "inchikey"
    if _CAS_RE.match(s):
        return "cas"
    if _SMILES_TOKENS.search(s):
        return "smiles"
    return "name"


def _resolve_unii(identifier: str, id_type: IdType) -> str | None:
    """
    Return a UNII string for the given identifier, or None if resolution fails.

    Raises ValueError for unsupported id_type values.
    """
    s = identifier.strip()

    if id_type == "unii":
        return s

    if id_type in ("smiles", "inchikey"):
        # Both SMILES and InChIKey are accepted by the structure search endpoint
        df = gsrs_structure_search(s, search_type="exact", top=1)
        if df is None or df.empty:
            return None
        unii = df["approval_id"].iloc[0]
        return unii if isinstance(unii, str) and unii.strip() else None

    if id_type == "cas":
        # CAS numbers are indexed as free-text codes in GSRS
        df = gsrs_search(s, top=1)
        if df is None or df.empty:
            return None
        unii = df["approval_id"].iloc[0]
        return unii if isinstance(unii, str) and unii.strip() else None

    if id_type == "name":
        df = gsrs_unii_from_name(s, top=1)
        if df is None or df.empty:
            return None
        unii = df["approval_id"].iloc[0]
        return unii if isinstance(unii, str) and unii.strip() else None

    raise ValueError(
        f"Unknown id_type {id_type!r}. "
        "Must be one of: 'auto', 'unii', 'smiles', 'inchikey', 'cas', 'name'."
    )


@graceful("GSRS structure-from-id lookup")
def gsrs_structure_from_id(
    identifier: str,
    id_type: IdType = "auto",
) -> pd.DataFrame | None:
    """
    Retrieve the chemical structure for a substance identified by any common
    identifier.

    The function first resolves the identifier to a UNII (using the
    appropriate GSRS endpoint for the identifier type) and then calls
    :func:`gsrs_structure`.

    Parameters
    ----------
    identifier:
        The substance identifier.  Accepted types:

        * **UNII** — 10-character FDA code (e.g. ``"R16CO5Y76E"``).
        * **SMILES** — e.g. ``"CC(=O)Oc1ccccc1C(=O)O"``.
        * **InChIKey** — 27-character key (e.g.
          ``"BSYNRYMUTXBXSQ-UHFFFAOYSA-N"``).
        * **CAS** — Registry Number (e.g. ``"50-78-2"``).
        * **Name** — INN, synonym, or any preferred name
          (e.g. ``"aspirin"``).

    id_type:
        How to interpret the identifier.  One of ``"auto"`` (default),
        ``"unii"``, ``"smiles"``, ``"inchikey"``, ``"cas"``, ``"name"``.
        ``"auto"`` infers the type from the string shape using pattern
        matching; supply an explicit value to override.

    Returns
    -------
    pandas.DataFrame
        Single-row data frame with SMILES, InChI, formula, etc.,
        or an empty DataFrame for non-chemical substances,
        or ``None`` on error / no match.
        Columns: ``smiles``, ``formula``, ``mwt``, ``inchi_key``,
        ``inchi``, ``stereochemistry``, ``optical_activity``,
        ``stereo_centers``, ``defined_stereo``, ``ez_centers``,
        ``charge``, ``molfile``, ``query``, ``date_retrieved``.

    Examples
    --------
    By UNII (direct lookup, no resolution step):

    >>> gsrs_structure_from_id("R16CO5Y76E")

    By name:

    >>> gsrs_structure_from_id("aspirin")
    >>> gsrs_structure_from_id("aspirin", id_type="name")

    By SMILES:

    >>> gsrs_structure_from_id("CC(=O)Oc1ccccc1C(=O)O")

    By InChIKey:

    >>> gsrs_structure_from_id("BSYNRYMUTXBXSQ-UHFFFAOYSA-N")

    By CAS number:

    >>> gsrs_structure_from_id("50-78-2")
    >>> gsrs_structure_from_id("50-78-2", id_type="cas")
    """
    if not isinstance(identifier, str) or not identifier.strip():
        raise ValueError("`identifier` must be a non-empty string.")

    effective_type: IdType = _detect(identifier) if id_type == "auto" else id_type

    unii = _resolve_unii(identifier, effective_type)
    if unii is None:
        warnings.warn(
            f"Could not resolve identifier {identifier!r} "
            f"(detected type: {effective_type!r}) to a UNII. Returning None.",
            stacklevel=2,
        )
        return None

    return gsrs_structure(unii)
