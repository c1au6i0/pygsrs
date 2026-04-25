"""
Async HTTP infrastructure for pygsrs.

Provides :func:`gsrs_get_async` for non-blocking API calls and
:func:`graceful_async` for the same error-handling pattern as
:func:`~pygsrs._base.graceful` but for ``async def`` functions.
"""

from __future__ import annotations

import asyncio
import functools
import random
import warnings
from collections.abc import Callable
from typing import Any

import httpx

BASE_URL = "https://gsrs.ncats.nih.gov/api/v1"

_RETRYABLE_CODES = {429, 500, 502, 503, 504}
_MAX_ATTEMPTS = 5


async def gsrs_get_async(
    path: str,
    params: dict[str, Any] | None = None,
    *,
    client: httpx.AsyncClient | None = None,
) -> httpx.Response:
    """
    Perform an async GET request against the GSRS API with retry logic.

    Parameters
    ----------
    path:
        URL path to append to the base URL.
    params:
        Query parameters dict.
    client:
        Optional :class:`httpx.AsyncClient` to reuse across calls.
        If ``None``, a new client is created per request.

    Returns
    -------
    httpx.Response

    Raises
    ------
    RuntimeError
        After exhausting all retries on retriable errors.
    httpx.HTTPStatusError
        Immediately on 4xx errors (no retry).
    """
    url = f"{BASE_URL}/{path.lstrip('/')}"

    async def _do(ac: httpx.AsyncClient) -> httpx.Response:
        for attempt in range(_MAX_ATTEMPTS):
            try:
                resp = await ac.get(url, params=params, timeout=30, follow_redirects=True)
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                if attempt < _MAX_ATTEMPTS - 1:
                    wait = min(2 ** attempt, 30) + random.uniform(0, 1)
                    await asyncio.sleep(wait)
                    continue
                raise RuntimeError(str(exc)) from exc

            if resp.status_code in _RETRYABLE_CODES:
                if attempt < _MAX_ATTEMPTS - 1:
                    wait = min(2 ** attempt, 30) + random.uniform(0, 1)
                    await asyncio.sleep(wait)
                    continue
                raise RuntimeError(f"HTTP {resp.status_code} after {_MAX_ATTEMPTS} attempts")

            resp.raise_for_status()
            return resp

        raise RuntimeError("Exhausted retries")  # pragma: no cover

    if client is not None:
        return await _do(client)
    async with httpx.AsyncClient() as ac:
        return await _do(ac)


def graceful_async(what: str) -> Callable:
    """
    Decorator factory for async functions.

    Wraps an ``async def`` function so that any exception is caught,
    a warning is issued, and ``None`` is returned.

    Parameters
    ----------
    what:
        Human-readable description used in the warning message.
    """
    def decorator(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            try:
                return await fn(*args, **kwargs)
            except Exception as exc:
                warnings.warn(
                    f"{what} failed. Returning None. The error was: {exc}",
                    stacklevel=2,
                )
                return None
        return wrapper
    return decorator
