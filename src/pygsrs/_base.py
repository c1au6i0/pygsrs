"""
Shared HTTP infrastructure for pygsrs.
"""

from __future__ import annotations

import random
import warnings
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

BASE_URL = "https://gsrs.ncats.nih.gov/api/v1"


def _jitter_wait(retry_state):
    """Exponential backoff with jitter (mirrors httr2's default)."""
    exp = wait_exponential(multiplier=1, min=1, max=30)(retry_state)
    return exp + random.uniform(0, 1)


def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in {429, 500, 502, 503, 504}
    return isinstance(exc, (httpx.TimeoutException, httpx.NetworkError))


class _RetryableError(Exception):
    """Wraps errors that should trigger a retry."""


def gsrs_get(path: str, params: dict[str, Any] | None = None) -> httpx.Response:
    """
    Perform a GET request against the GSRS API with retry logic.

    Only retries on network errors and 429/5xx responses.
    4xx errors (e.g. 404) are raised immediately without retrying.

    Parameters
    ----------
    path:
        URL path to append to the base URL (e.g. ``"substances/search"``).
    params:
        Query parameters dict.

    Returns
    -------
    httpx.Response

    Raises
    ------
    httpx.HTTPStatusError
        On a non-2xx response.
    """
    url = f"{BASE_URL}/{path.lstrip('/')}"

    @retry(
        retry=retry_if_exception_type(_RetryableError),
        stop=stop_after_attempt(5),
        wait=_jitter_wait,
        reraise=True,
    )
    def _do():
        try:
            resp = httpx.get(url, params=params, timeout=30, follow_redirects=True)
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            raise _RetryableError(str(exc)) from exc
        if resp.status_code in {429, 500, 502, 503, 504}:
            raise _RetryableError(f"HTTP {resp.status_code}")
        resp.raise_for_status()  # 4xx errors raised immediately — no retry
        return resp

    try:
        return _do()
    except _RetryableError as exc:
        # Exhausted retries on a retryable error — surface as a plain error
        raise RuntimeError(str(exc)) from exc


def graceful(what: str):
    """
    Decorator factory.  Wraps a function so that any exception is caught,
    a warning is issued, and ``None`` is returned — mirroring R's
    ``with_graceful_exit()``.

    Parameters
    ----------
    what:
        Human-readable description used in the warning message.
    """
    def decorator(fn):
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                warnings.warn(
                    f"{what} failed. Returning None. The error was: {exc}",
                    stacklevel=3,
                )
                return None
        wrapper.__name__ = fn.__name__
        wrapper.__doc__ = fn.__doc__
        return wrapper
    return decorator
