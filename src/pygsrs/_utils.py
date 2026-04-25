"""
Response-parsing utilities for pygsrs.

All ``parse_*`` functions accept the raw JSON-decoded data from the GSRS API
and return a ``pandas.DataFrame`` with normalised, snake_case column names.
The corresponding ``empty_*_df`` functions return zero-row DataFrames with
the correct column schema, used as fallbacks when the API returns no records.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

# ---------------------------------------------------------------------------
# Substances list (search / browse)
# ---------------------------------------------------------------------------

def parse_substances_response(data: dict, date_retrieved: str | None = None) -> pd.DataFrame:
    """
    Parse the ``content`` array from a substances search/browse response.

    Parameters
    ----------
    data:
        JSON-decoded response dict containing a ``"content"`` key with a
        list of substance records.
    date_retrieved:
        ISO 8601 timestamp to stamp each row with. Defaults to the current
        UTC time if not supplied.

    Returns
    -------
    pandas.DataFrame
        One row per substance with columns: ``uuid``, ``approval_id``,
        ``preferred_name``, ``substance_class``, ``status``,
        ``definition_type``, ``definition_level``, ``version``,
        ``names_url``, ``codes_url``, ``self_url``, ``date_retrieved``.
        Returns :func:`empty_substances_df` if there are no records.
    """
    if date_retrieved is None:
        date_retrieved = datetime.now(timezone.utc).isoformat()

    records = data.get("content", [])
    if not records:
        return empty_substances_df()

    rows = []
    for r in records:
        links = r.get("_self", "")
        rows.append({
            "uuid":             r.get("uuid"),
            "approval_id":      r.get("approvalID"),
            "preferred_name":   r.get("_name") or r.get("preferred_name"),
            "substance_class":  r.get("substanceClass"),
            "status":           r.get("status"),
            "definition_type":  r.get("definitionType"),
            "definition_level": r.get("definitionLevel"),
            "version":          r.get("version"),
            "names_url":        r.get("_names"),
            "codes_url":        r.get("_codes"),
            "self_url":         links,
            "date_retrieved":   date_retrieved,
        })

    return pd.DataFrame(rows)


def empty_substances_df() -> pd.DataFrame:
    """Return a zero-row DataFrame with the substances schema."""
    return pd.DataFrame(columns=[
        "uuid", "approval_id", "preferred_name", "substance_class",
        "status", "definition_type", "definition_level", "version",
        "names_url", "codes_url", "self_url", "date_retrieved",
    ])


# ---------------------------------------------------------------------------
# Names
# ---------------------------------------------------------------------------

def parse_names_response(data: list[dict], query: str, date_retrieved: str | None = None) -> pd.DataFrame:
    """
    Parse a list of name records from the ``/substances({unii})/names`` endpoint.

    Parameters
    ----------
    data:
        List of name record dicts as returned by the GSRS API.
    query:
        The UNII used for the lookup; added as a ``query`` column.
    date_retrieved:
        ISO 8601 timestamp. Defaults to the current UTC time.

    Returns
    -------
    pandas.DataFrame
        One row per name with columns: ``name``, ``type``, ``language``,
        ``preferred``, ``display_name``, ``query``, ``date_retrieved``.
        Returns :func:`empty_names_df` if ``data`` is empty.
    """
    if date_retrieved is None:
        date_retrieved = datetime.now(timezone.utc).isoformat()

    if not data:
        return empty_names_df()

    rows = []
    for r in data:
        rows.append({
            "name":           r.get("name"),
            "type":           r.get("type"),
            "language":       r.get("language"),
            "preferred":      r.get("preferred"),
            "display_name":   r.get("displayName"),
            "query":          query,
            "date_retrieved": date_retrieved,
        })
    return pd.DataFrame(rows)


def empty_names_df() -> pd.DataFrame:
    """Return a zero-row DataFrame with the names schema."""
    return pd.DataFrame(columns=[
        "name", "type", "language", "preferred", "display_name",
        "query", "date_retrieved",
    ])


# ---------------------------------------------------------------------------
# Codes
# ---------------------------------------------------------------------------

def parse_codes_response(data: list[dict], query: str, date_retrieved: str | None = None) -> pd.DataFrame:
    """
    Parse a list of code records from the ``/substances({unii})/codes`` endpoint.

    Parameters
    ----------
    data:
        List of code record dicts as returned by the GSRS API.
    query:
        The UNII used for the lookup; added as a ``query`` column.
    date_retrieved:
        ISO 8601 timestamp. Defaults to the current UTC time.

    Returns
    -------
    pandas.DataFrame
        One row per code with columns: ``code_system``, ``code``,
        ``type``, ``url``, ``query``, ``date_retrieved``.
        Returns :func:`empty_codes_df` if ``data`` is empty.
    """
    if date_retrieved is None:
        date_retrieved = datetime.now(timezone.utc).isoformat()

    if not data:
        return empty_codes_df()

    rows = []
    for r in data:
        rows.append({
            "code_system":    r.get("codeSystem"),
            "code":           r.get("code"),
            "type":           r.get("type"),
            "url":            r.get("url"),
            "query":          query,
            "date_retrieved": date_retrieved,
        })
    return pd.DataFrame(rows)


def empty_codes_df() -> pd.DataFrame:
    """Return a zero-row DataFrame with the codes schema."""
    return pd.DataFrame(columns=[
        "code_system", "code", "type", "url", "query", "date_retrieved",
    ])


# ---------------------------------------------------------------------------
# Structure
# ---------------------------------------------------------------------------

def parse_structure_response(data: dict, query: str, date_retrieved: str | None = None) -> pd.DataFrame:
    """
    Parse the ``structure`` sub-object from a ``/substances({unii})`` response.

    Parameters
    ----------
    data:
        Full substance record dict; the ``"structure"`` key is extracted.
    query:
        The UNII used for the lookup; added as a ``query`` column.
    date_retrieved:
        ISO 8601 timestamp. Defaults to the current UTC time.

    Returns
    -------
    pandas.DataFrame
        Single-row DataFrame with columns: ``smiles``, ``formula``,
        ``mwt``, ``inchi_key``, ``inchi``, ``stereochemistry``,
        ``optical_activity``, ``stereo_centers``, ``defined_stereo``,
        ``ez_centers``, ``charge``, ``molfile``, ``query``,
        ``date_retrieved``.
        Returns :func:`empty_structure_df` if no structure is present
        (e.g. for biological substances).
    """
    if date_retrieved is None:
        date_retrieved = datetime.now(timezone.utc).isoformat()

    s = data.get("structure")
    if not s:
        return empty_structure_df()

    return pd.DataFrame([{
        "smiles":           s.get("smiles"),
        "formula":          s.get("formula"),
        "mwt":              s.get("mwt"),
        "inchi_key":        s.get("_inchiKey"),
        "inchi":            s.get("_inchi"),
        "stereochemistry":  s.get("stereochemistry"),
        "optical_activity": s.get("opticalActivity"),
        "stereo_centers":   s.get("stereoCenters"),
        "defined_stereo":   s.get("definedStereo"),
        "ez_centers":       s.get("ezCenters"),
        "charge":           s.get("charge"),
        "molfile":          s.get("molfile"),
        "query":            query,
        "date_retrieved":   date_retrieved,
    }])


def empty_structure_df() -> pd.DataFrame:
    """Return a zero-row DataFrame with the structure schema."""
    return pd.DataFrame(columns=[
        "smiles", "formula", "mwt", "inchi_key", "inchi",
        "stereochemistry", "optical_activity", "stereo_centers",
        "defined_stereo", "ez_centers", "charge", "molfile",
        "query", "date_retrieved",
    ])


# ---------------------------------------------------------------------------
# Hierarchy
# ---------------------------------------------------------------------------

def parse_hierarchy_response(data: list[dict], query: str, date_retrieved: str | None = None) -> pd.DataFrame:
    """
    Parse a list of hierarchy nodes from the ``/substances({unii})/@hierarchy`` endpoint.

    Parameters
    ----------
    data:
        List of hierarchy node dicts as returned by the GSRS API.
    query:
        The UNII used for the lookup; added as a ``query`` column.
    date_retrieved:
        ISO 8601 timestamp. Defaults to the current UTC time.

    Returns
    -------
    pandas.DataFrame
        One row per node with columns: ``text``, ``type``, ``depth``,
        ``expandable``, ``node_id``, ``parent``, ``approval_id``,
        ``name``, ``refuuid``, ``substance_class``, ``deprecated``,
        ``query``, ``date_retrieved``.
        Returns :func:`empty_hierarchy_df` if ``data`` is empty.
    """
    if date_retrieved is None:
        date_retrieved = datetime.now(timezone.utc).isoformat()

    if not data:
        return empty_hierarchy_df()

    rows = []
    for node in data:
        val = node.get("value") or {}
        rows.append({
            "text":            node.get("text"),
            "type":            node.get("type"),
            "depth":           node.get("depth"),
            "expandable":      node.get("expandable"),
            "node_id":         node.get("id"),
            "parent":          node.get("parent"),
            "approval_id":     val.get("approvalID"),
            "name":            val.get("name"),
            "refuuid":         val.get("refuuid"),
            "substance_class": val.get("substanceClass"),
            "deprecated":      val.get("deprecated"),
            "query":           query,
            "date_retrieved":  date_retrieved,
        })
    return pd.DataFrame(rows)


def empty_hierarchy_df() -> pd.DataFrame:
    """Return a zero-row DataFrame with the hierarchy schema."""
    return pd.DataFrame(columns=[
        "text", "type", "depth", "expandable", "node_id", "parent",
        "approval_id", "name", "refuuid", "substance_class", "deprecated",
        "query", "date_retrieved",
    ])


# ---------------------------------------------------------------------------
# Vocabularies
# ---------------------------------------------------------------------------

def parse_vocabularies_response(data: list[dict], date_retrieved: str | None = None) -> pd.DataFrame:
    """
    Parse a list of vocabulary domain records from the ``/vocabularies`` endpoint.

    Each domain contains multiple terms; this function flattens them so each
    row represents one term within one domain.

    Parameters
    ----------
    data:
        List of vocabulary domain dicts, each containing a ``"terms"`` list.
    date_retrieved:
        ISO 8601 timestamp. Defaults to the current UTC time.

    Returns
    -------
    pandas.DataFrame
        One row per term with columns: ``domain``, ``term_type``,
        ``value``, ``display``, ``hidden``, ``selected``,
        ``date_retrieved``.
        Returns :func:`empty_vocabularies_df` if ``data`` is empty.
    """
    if date_retrieved is None:
        date_retrieved = datetime.now(timezone.utc).isoformat()

    if not data:
        return empty_vocabularies_df()

    rows = []
    for vocab in data:
        domain = vocab.get("domain", "")
        term_type = vocab.get("vocabularyTermType", "")
        for term in vocab.get("terms", []):
            rows.append({
                "domain":          domain,
                "term_type":       term_type,
                "value":           term.get("value"),
                "display":         term.get("display"),
                "hidden":          term.get("hidden"),
                "selected":        term.get("selected"),
                "date_retrieved":  date_retrieved,
            })
    return pd.DataFrame(rows)


def empty_vocabularies_df() -> pd.DataFrame:
    """Return a zero-row DataFrame with the vocabularies schema."""
    return pd.DataFrame(columns=[
        "domain", "term_type", "value", "display",
        "hidden", "selected", "date_retrieved",
    ])
