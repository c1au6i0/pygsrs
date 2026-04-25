"""gsrs_batch — fetch substance data for multiple UNIIs concurrently."""

from __future__ import annotations

import warnings
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd

from ._base import graceful
from .substance import gsrs_substance


@graceful("GSRS batch lookup")
def gsrs_batch(
    uniis: Sequence[str],
    workers: int = 8,
) -> pd.DataFrame | None:
    """
    Fetch substance records for multiple UNIIs concurrently.

    Each UNII is looked up via :func:`gsrs_substance` in a thread pool.
    Failed individual lookups are skipped with a warning; only successfully
    retrieved records are included in the result.

    Parameters
    ----------
    uniis:
        Sequence of FDA UNII codes to look up.
    workers:
        Maximum number of concurrent threads. Default 8.

    Returns
    -------
    pandas.DataFrame
        Combined DataFrame with one row per successfully retrieved substance,
        or ``None`` on error. The ``query`` column holds the input UNII for
        each row.

    Examples
    --------
    >>> uniis = ["R16CO5Y76E", "6M3C89ZY6R"]  # aspirin, nicotine
    >>> df = gsrs_batch(uniis)
    >>> len(df)
    2

    >>> df[["approval_id", "preferred_name"]]
    """
    if not uniis:
        raise ValueError("`uniis` must be a non-empty sequence.")

    frames: list[pd.DataFrame] = []

    with ThreadPoolExecutor(max_workers=workers) as pool:
        future_to_unii = {pool.submit(gsrs_substance, u): u for u in uniis}
        for future in as_completed(future_to_unii):
            unii = future_to_unii[future]
            result = future.result()
            if result is not None and len(result) > 0:
                frames.append(result)
            elif result is None:
                warnings.warn(
                    f"gsrs_batch: lookup for UNII '{unii}' failed and was skipped.",
                    stacklevel=2,
                )

    if not frames:
        from ._utils import empty_substances_df
        return empty_substances_df()

    return pd.concat(frames, ignore_index=True)
