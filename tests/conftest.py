"""
Shared pytest fixtures and mock data for pygsrs tests.

All tests use pytest-httpx to intercept HTTP calls so the suite
runs fully offline without touching the live GSRS API.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Reference constants
# ---------------------------------------------------------------------------

ASPIRIN_UNII = "R16CO5Y76E"
ASPIRIN_SMILES = "CC(=O)Oc1ccccc1C(=O)O"
ASPIRIN_NAME = "ASPIRIN"

NICOTINE_UNII = "6M3C89ZY6R"
NICOTINE_NAME = "NICOTINE"

BASE = "https://gsrs.ncats.nih.gov/api/v1"

# ---------------------------------------------------------------------------
# Mock API payloads
# ---------------------------------------------------------------------------

SUBSTANCE_RECORD = {
    "uuid": "0d77a7ed-f9e5-41a2-b515-7b7dc78e2f65",
    "approvalID": ASPIRIN_UNII,
    "_name": ASPIRIN_NAME,
    "substanceClass": "chemical",
    "status": "approved",
    "definitionType": "PRIMARY",
    "definitionLevel": "COMPLETE",
    "version": "1",
    "_names": f"{BASE}/substances({ASPIRIN_UNII})/names",
    "_codes": f"{BASE}/substances({ASPIRIN_UNII})/codes",
    "_self": f"{BASE}/substances({ASPIRIN_UNII})",
}

SUBSTANCES_ENVELOPE = {"content": [SUBSTANCE_RECORD], "total": 1, "count": 1, "skip": 0}

NAMES_LIST = [
    {"name": "ASPIRIN", "type": "cn", "language": "en", "preferred": True, "displayName": True},
    {"name": "Acetylsalicylic acid", "type": "sys", "language": "en", "preferred": False, "displayName": False},
]

CODES_LIST = [
    {"codeSystem": "CAS", "code": "50-78-2", "type": "PRIMARY", "url": None},
    {"codeSystem": "NCI", "code": "C26223", "type": "PRIMARY", "url": None},
]

SUBSTANCE_FULL = {
    **SUBSTANCE_RECORD,
    "structure": {
        "smiles": ASPIRIN_SMILES,
        "formula": "C9H8O4",
        "mwt": 180.16,
        "_inchiKey": "BSYNRYMUTXBXSQ-UHFFFAOYSA-N",
        "_inchi": "InChI=1S/C9H8O4/c1-6(10)13-8-5-3-2-4-7(8)9(11)12/h2-5H,1H3,(H,11,12)",
        "stereochemistry": "ACHIRAL",
        "opticalActivity": "NONE",
        "stereoCenters": 0,
        "definedStereo": 0,
        "ezCenters": 0,
        "charge": 0,
        "molfile": "\n  Mrv2211 01012400002D\n...",
    },
}

HIERARCHY_LIST = [
    {
        "text": "ASPIRIN",
        "type": "substance",
        "depth": 0,
        "expandable": False,
        "id": "node-001",
        "parent": None,
        "value": {
            "approvalID": ASPIRIN_UNII,
            "name": ASPIRIN_NAME,
            "refuuid": SUBSTANCE_RECORD["uuid"],
            "substanceClass": "chemical",
            "deprecated": False,
        },
    }
]

VOCABULARIES_LIST = [
    {
        "domain": "SUBSTANCE_CLASS",
        "vocabularyTermType": "ix.ginas.models.v1.Substance",
        "terms": [
            {"value": "chemical", "display": "Chemical", "hidden": False, "selected": False},
            {"value": "protein", "display": "Protein", "hidden": False, "selected": False},
        ],
    }
]
