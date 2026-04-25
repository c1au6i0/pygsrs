"""
Optional disk-based HTTP caching for pygsrs.

Uses :mod:`diskcache` (``pip install pygsrs[cache]``) to cache API responses
and avoid redundant network requests for repeated lookups.

Usage::

    import pygsrs
    pygsrs.enable_cache()                       # ~/.cache/pygsrs, no expiry
    pygsrs.enable_cache(directory="/tmp/c", ttl=3600)
    pygsrs.disable_cache()
    pygsrs.clear_cache()
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import httpx

from ._base import BASE_URL

# Module-level state
_cache: Any = None        # diskcache.Cache instance or None
_cache_ttl: int | None = None


def enable_cache(
    directory: str | Path | None = None,
    ttl: int | None = None,
) -> None:
    """
    Enable disk-based HTTP response caching.

    Requires the ``cache`` optional dependency:
    ``pip install pygsrs[cache]``.

    Parameters
    ----------
    directory:
        Path to cache directory. Defaults to ``~/.cache/pygsrs``.
    ttl:
        Time-to-live in seconds. ``None`` means entries never expire.

    Examples
    --------
    >>> import pygsrs
    >>> pygsrs.enable_cache()
    >>> pygsrs.enable_cache(directory="/tmp/mygsrs", ttl=3600)
    """
    global _cache, _cache_ttl
    try:
        import diskcache
    except ImportError as exc:
        raise ImportError(
            "Caching requires the 'diskcache' package. "
            "Install it with: pip install pygsrs[cache]"
        ) from exc

    if directory is None:
        directory = Path.home() / ".cache" / "pygsrs"
    _cache = diskcache.Cache(str(directory))
    _cache_ttl = ttl


def disable_cache() -> None:
    """
    Disable caching.  Subsequent API calls will not use or update the cache.

    Examples
    --------
    >>> import pygsrs
    >>> pygsrs.disable_cache()
    """
    global _cache
    _cache = None


def clear_cache() -> None:
    """
    Clear all entries from the cache.

    The cache must be enabled first with :func:`enable_cache`.

    Examples
    --------
    >>> import pygsrs
    >>> pygsrs.enable_cache()
    >>> pygsrs.clear_cache()
    """
    if _cache is not None:
        _cache.clear()


def _cache_key(url: str, params: dict | None) -> str:
    """Generate a stable cache key from URL + params."""
    raw = json.dumps({"url": url, "params": params or {}}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


def cached_gsrs_get(path: str, params: dict[str, Any] | None = None) -> httpx.Response:
    """
    Wrapper around :func:`~pygsrs._base.gsrs_get` that checks the cache first.

    If caching is disabled (default), this is a transparent pass-through.

    Parameters
    ----------
    path:
        URL path (same as :func:`~pygsrs._base.gsrs_get`).
    params:
        Query parameters dict.

    Returns
    -------
    httpx.Response
    """
    from ._base import gsrs_get

    if _cache is None:
        return gsrs_get(path, params)

    url = f"{BASE_URL}/{path.lstrip('/')}"
    key = _cache_key(url, params)

    if key in _cache:
        # Reconstruct a minimal response from cached data
        cached = _cache[key]
        # Return a mock response wrapping the cached JSON bytes
        return _CachedResponse(cached)

    resp = gsrs_get(path, params)
    # Cache raw bytes to avoid re-serialising
    try:
        _cache.set(key, resp.content, expire=_cache_ttl)
    except Exception:
        pass  # Cache write failure is non-fatal
    return resp


class _CachedResponse:
    """Minimal httpx.Response-compatible object backed by cached bytes."""

    def __init__(self, content: bytes) -> None:
        self._content = content

    def json(self) -> Any:
        return json.loads(self._content)

    @property
    def content(self) -> bytes:
        return self._content

    @property
    def status_code(self) -> int:
        return 200
