"""Tests for the caching integration in pygsrs._cache / pygsrs._base."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from conftest import ASPIRIN_UNII, BASE, SUBSTANCES_ENVELOPE

from pygsrs import _cache as _cache_module
from pygsrs import clear_cache, disable_cache, enable_cache, gsrs_substance

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _FakeCache(dict):
    """A simple dict that also exposes .set() and .clear() like diskcache.Cache."""

    def set(self, key, value, expire=None):
        self[key] = value

    def clear(self):
        super().clear()


def _enable_fake_cache():
    """Activate a fake in-memory cache (bypasses diskcache import)."""
    _cache_module._cache = _FakeCache()
    _cache_module._cache_ttl = None


def _disable_fake_cache():
    _cache_module._cache = None


# ---------------------------------------------------------------------------
# enable_cache / disable_cache / clear_cache
# ---------------------------------------------------------------------------

def test_enable_cache_raises_without_diskcache():
    """enable_cache() must raise ImportError when diskcache is not installed."""
    with patch.dict("sys.modules", {"diskcache": None}):
        with pytest.raises(ImportError, match="diskcache"):
            enable_cache()


def test_disable_cache_sets_none():
    _enable_fake_cache()
    assert _cache_module._cache is not None
    disable_cache()
    assert _cache_module._cache is None


def test_clear_cache_empties_store():
    _enable_fake_cache()
    fake = _cache_module._cache
    fake["sentinel"] = b"data"
    assert len(fake) == 1
    clear_cache()
    assert len(fake) == 0
    _disable_fake_cache()


def test_clear_cache_noop_when_disabled():
    """clear_cache() must not raise when caching is disabled."""
    _disable_fake_cache()
    clear_cache()  # should not raise


# ---------------------------------------------------------------------------
# Integration: gsrs_get routes through cache
# ---------------------------------------------------------------------------

def test_gsrs_get_stores_response_in_cache(httpx_mock):
    """A fresh request should be stored in the cache."""
    httpx_mock.add_response(
        url=f"{BASE}/substances/search?q=root_approvalID%3A{ASPIRIN_UNII}&top=1",
        json=SUBSTANCES_ENVELOPE,
    )
    _enable_fake_cache()
    try:
        result = gsrs_substance(ASPIRIN_UNII)
        assert result is not None and not result.empty
        assert len(_cache_module._cache) == 1, "Response should be stored in cache"
    finally:
        _disable_fake_cache()


def test_gsrs_get_returns_cached_response(httpx_mock):
    """A second identical request should be served from cache without a new HTTP call."""
    httpx_mock.add_response(
        url=f"{BASE}/substances/search?q=root_approvalID%3A{ASPIRIN_UNII}&top=1",
        json=SUBSTANCES_ENVELOPE,
    )
    _enable_fake_cache()
    try:
        # First call — populates the cache
        gsrs_substance(ASPIRIN_UNII)
        # Second call — should be served from cache (no additional mock needed)
        result = gsrs_substance(ASPIRIN_UNII)
        assert result is not None and not result.empty
    finally:
        _disable_fake_cache()


def test_gsrs_get_bypasses_cache_when_disabled(httpx_mock):
    """When cache is disabled, every call goes to the network."""
    httpx_mock.add_response(
        url=f"{BASE}/substances/search?q=root_approvalID%3A{ASPIRIN_UNII}&top=1",
        json=SUBSTANCES_ENVELOPE,
    )
    httpx_mock.add_response(
        url=f"{BASE}/substances/search?q=root_approvalID%3A{ASPIRIN_UNII}&top=1",
        json=SUBSTANCES_ENVELOPE,
    )
    _disable_fake_cache()
    # Both calls hit the network; httpx_mock would raise if more than 2 are made
    gsrs_substance(ASPIRIN_UNII)
    gsrs_substance(ASPIRIN_UNII)
