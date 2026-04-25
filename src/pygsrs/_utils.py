"""
Response-parsing utilities for pygsrs.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

import pandas as pd


# ---------------------------------------------------------------------------
# Column name normalisation (mirrors janitor::clean_names)
# ---------------------------------------------------------------------------

def _clean_name(s: str) -> str:
    s = re.sub(r"[^0-9a-zA-Z]+", "_", s)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    s = s.lower().strip("_")
    return s


def clean_names(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [_clean_name(c) for c in df.columns]
    return df


# ---------------------------------------------------------------------------
# Substances list (search / browse)
# ---------------------------------------------------------------------------

_SUBSTANCE_FIELDS = [
    "uuid", "approvalID", "preferred_name", "substanceClass",
    "status", "definitionType", "definitionLevel", "version",
    "_names", "_codes", "_self",
]


def parse_substances_response(data: dict, date_retrieved: str | None = None) -> pd.DataFrame:
    """Parse the ``content`` array from a substances search/browse response."""
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
    return pd.DataFrame(columns=[
        "uuid", "approval_id", "preferred_name", "substance_class",
        "status", "definition_type", "definition_level", "version",
        "names_url", "codes_url", "self_url", "date_retrieved",
    ])


# ---------------------------------------------------------------------------
# Names
# ---------------------------------------------------------------------------

def parse_names_response(data: list[dict], query: str, date_retrieved: str | None = None) -> pd.DataFrame:
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
    return pd.DataFrame(columns=[
        "name", "type", "language", "preferred", "display_name",
        "query", "date_retrieved",
    ])


# ---------------------------------------------------------------------------
# Codes
# ---------------------------------------------------------------------------

def parse_codes_response(data: list[dict], query: str, date_retrieved: str | None = None) -> pd.DataFrame:
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
    return pd.DataFrame(columns=[
        "code_system", "code", "type", "url", "query", "date_retrieved",
    ])


# ---------------------------------------------------------------------------
# Structure
# ---------------------------------------------------------------------------

def parse_structure_response(data: dict, query: str, date_retrieved: str | None = None) -> pd.DataFrame:
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
    return pd.DataFrame(columns=[
        "text", "type", "depth", "expandable", "node_id", "parent",
        "approval_id", "name", "refuuid", "substance_class", "deprecated",
        "query", "date_retrieved",
    ])


# ---------------------------------------------------------------------------
# Vocabularies
# ---------------------------------------------------------------------------

def parse_vocabularies_response(data: list[dict], date_retrieved: str | None = None) -> pd.DataFrame:
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
    return pd.DataFrame(columns=[
        "domain", "term_type", "value", "display",
        "hidden", "selected", "date_retrieved",
    ])
