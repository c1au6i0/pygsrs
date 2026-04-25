"""gsrs_vocabularies — retrieve all GSRS controlled vocabulary terms."""

from __future__ import annotations

import pandas as pd

from ._base import graceful, gsrs_get
from ._utils import parse_vocabularies_response


@graceful("GSRS vocabularies lookup")
def gsrs_vocabularies() -> pd.DataFrame | None:
    """
    Retrieve all controlled vocabulary domains and their terms from GSRS.

    Vocabularies define the valid values for fields like ``substanceClass``,
    name ``type``, code ``codeSystem``, and others. This is useful for
    understanding what filter values are available in search queries.

    Returns
    -------
    pandas.DataFrame
        One row per term across all vocabulary domains,
        or ``None`` on error.
        Columns: ``domain``, ``term_type``, ``value``, ``display``,
        ``hidden``, ``selected``, ``date_retrieved``.

    Examples
    --------
    >>> vocab = gsrs_vocabularies()
    >>> vocab["domain"].unique()

    Get all valid substance classes:

    >>> substance_classes = vocab[vocab["domain"] == "SUBSTANCE_CLASS"]["value"]
    """
    data = gsrs_get("vocabularies").json()
    # API returns either a list directly or {"content": [...]}
    if isinstance(data, dict):
        data = data.get("content", [])
    return parse_vocabularies_response(data)
