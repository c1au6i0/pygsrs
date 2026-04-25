"""
pygsrs — Python client for the FDA Global Substance Registration System (GSRS).

Public API
----------
All sync functions return ``pandas.DataFrame`` (or a dict of them for
:func:`gsrs_all`). On error, they return ``None`` and emit a warning.
Async equivalents are prefixed with ``a`` (e.g. :func:`agsrs_substance`).

Sync Functions
~~~~~~~~~~~~~~
- :func:`gsrs_search` — free-text search
- :func:`gsrs_search_all` — auto-paginated free-text search
- :func:`gsrs_substance` — look up by UNII
- :func:`gsrs_batch` — batch lookup for multiple UNIIs
- :func:`gsrs_names` — all names for a substance
- :func:`gsrs_codes` — all external codes for a substance
- :func:`gsrs_structure` — chemical structure data
- :func:`gsrs_structure_search` — search by SMILES
- :func:`gsrs_hierarchy` — relationship hierarchy
- :func:`gsrs_browse` — paginated browse
- :func:`gsrs_browse_all` — auto-paginated browse
- :func:`gsrs_vocabularies` — controlled vocabulary terms
- :func:`gsrs_unii_from_name` — look up UNII by name
- :func:`gsrs_all` — everything at once

Async Functions
~~~~~~~~~~~~~~~
- :func:`agsrs_search`
- :func:`agsrs_substance`
- :func:`agsrs_names`
- :func:`agsrs_codes`
- :func:`agsrs_structure`
- :func:`agsrs_structure_search`
- :func:`agsrs_hierarchy`
- :func:`agsrs_browse`
- :func:`agsrs_vocabularies`
- :func:`agsrs_unii_from_name`
- :func:`agsrs_all`

Caching
~~~~~~~
- :func:`enable_cache` — enable disk-based HTTP caching
- :func:`disable_cache` — disable caching
- :func:`clear_cache` — clear the cache

Configuration
~~~~~~~~~~~~~
- :func:`set_base_url` — point at a custom GSRS instance
"""

from ._async_api import (
    agsrs_all,
    agsrs_browse,
    agsrs_codes,
    agsrs_hierarchy,
    agsrs_names,
    agsrs_search,
    agsrs_structure,
    agsrs_structure_search,
    agsrs_substance,
    agsrs_unii_from_name,
    agsrs_vocabularies,
)
from ._cache import clear_cache, disable_cache, enable_cache
from .all import gsrs_all
from .batch import gsrs_batch
from .browse import gsrs_browse
from .codes import gsrs_codes
from .hierarchy import gsrs_hierarchy
from .names import gsrs_names
from .pagination import gsrs_browse_all, gsrs_search_all
from .search import gsrs_search
from .structure import gsrs_structure
from .structure_search import gsrs_structure_search
from .substance import gsrs_substance
from .unii_from_name import gsrs_unii_from_name
from .vocabularies import gsrs_vocabularies


def set_base_url(url: str | None = None) -> None:
    """
    Override the GSRS base URL (e.g. for a private deployment).

    Parameters
    ----------
    url:
        Full base URL including ``/api/v1``.  Pass ``None`` to reset to
        the public FDA instance.

    Examples
    --------
    >>> import pygsrs
    >>> pygsrs.set_base_url("https://my-gsrs.example.com/api/v1")
    >>> pygsrs.set_base_url()  # reset to public FDA instance
    """
    from . import _async_base, _base
    default = "https://gsrs.ncats.nih.gov/api/v1"
    _base.BASE_URL = url if url is not None else default
    _async_base.BASE_URL = url if url is not None else default


__all__ = [
    # Sync
    "gsrs_search",
    "gsrs_search_all",
    "gsrs_substance",
    "gsrs_batch",
    "gsrs_names",
    "gsrs_codes",
    "gsrs_structure",
    "gsrs_structure_search",
    "gsrs_hierarchy",
    "gsrs_browse",
    "gsrs_browse_all",
    "gsrs_vocabularies",
    "gsrs_unii_from_name",
    "gsrs_all",
    # Async
    "agsrs_search",
    "agsrs_substance",
    "agsrs_names",
    "agsrs_codes",
    "agsrs_structure",
    "agsrs_structure_search",
    "agsrs_hierarchy",
    "agsrs_browse",
    "agsrs_vocabularies",
    "agsrs_unii_from_name",
    "agsrs_all",
    # Caching
    "enable_cache",
    "disable_cache",
    "clear_cache",
    # Config
    "set_base_url",
]
