"""
pygsrs — Python client for the FDA Global Substance Registration System (GSRS).

Public API
----------
All functions return ``pandas.DataFrame`` (or a dict of them for
:func:`gsrs_all`). On error, they return ``None`` and emit a warning.

Functions
~~~~~~~~~
- :func:`gsrs_search` — free-text search
- :func:`gsrs_substance` — look up by UNII
- :func:`gsrs_names` — all names for a substance
- :func:`gsrs_codes` — all external codes for a substance
- :func:`gsrs_structure` — chemical structure data
- :func:`gsrs_structure_search` — search by SMILES
- :func:`gsrs_hierarchy` — relationship hierarchy
- :func:`gsrs_browse` — paginated browse
- :func:`gsrs_vocabularies` — controlled vocabulary terms
- :func:`gsrs_unii_from_name` — look up UNII by name
- :func:`gsrs_all` — everything at once
"""

from .search import gsrs_search
from .substance import gsrs_substance
from .names import gsrs_names
from .codes import gsrs_codes
from .structure import gsrs_structure
from .structure_search import gsrs_structure_search
from .hierarchy import gsrs_hierarchy
from .browse import gsrs_browse
from .vocabularies import gsrs_vocabularies
from .unii_from_name import gsrs_unii_from_name
from .all import gsrs_all

__all__ = [
    "gsrs_search",
    "gsrs_substance",
    "gsrs_names",
    "gsrs_codes",
    "gsrs_structure",
    "gsrs_structure_search",
    "gsrs_hierarchy",
    "gsrs_browse",
    "gsrs_vocabularies",
    "gsrs_unii_from_name",
    "gsrs_all",
]
