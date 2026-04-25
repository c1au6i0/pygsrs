"""
pygsrs command-line interface.

Provides quick substance lookups from the terminal.

Usage
-----
.. code-block:: bash

    pygsrs search aspirin
    pygsrs substance R16CO5Y76E
    pygsrs names R16CO5Y76E
    pygsrs codes R16CO5Y76E
    pygsrs structure R16CO5Y76E
    pygsrs structure-search "CC(=O)Oc1ccccc1C(=O)O" --type exact
    pygsrs hierarchy R16CO5Y76E
    pygsrs browse --top 20
    pygsrs unii-from-name aspirin
    pygsrs all R16CO5Y76E

Output formats: ``table`` (default), ``csv``, ``json``.
"""

from __future__ import annotations

import argparse
import sys

import pandas as pd


def _print(df: pd.DataFrame | dict | None, fmt: str) -> None:
    """Print a DataFrame or dict of DataFrames in the requested format."""
    if df is None:
        print("No results (or an error occurred). Check warnings above.", file=sys.stderr)
        sys.exit(1)

    if isinstance(df, dict):
        for key, val in df.items():
            print(f"\n--- {key} ---")
            if val is None or (isinstance(val, pd.DataFrame) and val.empty):
                print("(no data)")
            else:
                _print_df(val, fmt)
        return

    _print_df(df, fmt)


def _print_df(df: pd.DataFrame, fmt: str) -> None:
    if fmt == "csv":
        print(df.to_csv(index=False))
    elif fmt == "json":
        print(df.to_json(orient="records", indent=2))
    else:
        pd.set_option("display.max_columns", None)
        pd.set_option("display.width", None)
        print(df.to_string(index=False))


def _add_format(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--format", choices=["table", "csv", "json"], default="table",
        help="Output format (default: table)",
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="pygsrs",
        description="Query the FDA Global Substance Registration System (GSRS) API.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # search
    p = sub.add_parser("search", help="Full-text search of substances.")
    p.add_argument("query", help="Lucene query string (e.g. 'aspirin').")
    p.add_argument("--top", type=int, default=10, help="Max results (default 10).")
    p.add_argument("--skip", type=int, default=0, help="Records to skip (default 0).")
    _add_format(p)

    # substance
    p = sub.add_parser("substance", help="Look up a substance by UNII.")
    p.add_argument("unii", help="FDA UNII code (e.g. R16CO5Y76E).")
    _add_format(p)

    # names
    p = sub.add_parser("names", help="Get all names for a substance.")
    p.add_argument("unii", help="FDA UNII code.")
    _add_format(p)

    # codes
    p = sub.add_parser("codes", help="Get all external codes for a substance.")
    p.add_argument("unii", help="FDA UNII code.")
    _add_format(p)

    # structure
    p = sub.add_parser("structure", help="Get chemical structure data.")
    p.add_argument("unii", help="FDA UNII code.")
    _add_format(p)

    # structure-search
    p = sub.add_parser("structure-search", help="Search by SMILES.")
    p.add_argument("smiles", help="SMILES string.")
    p.add_argument("--type", dest="search_type", default="sub",
                   choices=["sub", "sim", "exact", "flex"],
                   help="Search type (default: sub).")
    p.add_argument("--cutoff", type=float, default=0.8,
                   help="Tanimoto cutoff for similarity search (default 0.8).")
    p.add_argument("--top", type=int, default=10, help="Max results (default 10).")
    _add_format(p)

    # hierarchy
    p = sub.add_parser("hierarchy", help="Get relationship hierarchy.")
    p.add_argument("unii", help="FDA UNII code.")
    _add_format(p)

    # browse
    p = sub.add_parser("browse", help="Browse all substances (paginated).")
    p.add_argument("--top", type=int, default=10, help="Records to return (default 10).")
    p.add_argument("--skip", type=int, default=0, help="Records to skip (default 0).")
    _add_format(p)

    # vocabularies
    p = sub.add_parser("vocabularies", help="List all controlled vocabulary terms.")
    _add_format(p)

    # unii-from-name
    p = sub.add_parser("unii-from-name", help="Look up UNII by substance name.")
    p.add_argument("name", help="Substance name (e.g. 'aspirin').")
    p.add_argument("--top", type=int, default=5, help="Max candidates (default 5).")
    _add_format(p)

    # all
    p = sub.add_parser("all", help="Get all data for a substance.")
    p.add_argument("unii", help="FDA UNII code.")
    _add_format(p)

    args = parser.parse_args(argv)
    fmt: str = args.format

    # Lazy imports to keep startup fast
    import warnings
    warnings.simplefilter("always")

    from pygsrs import (
        gsrs_all,
        gsrs_browse,
        gsrs_codes,
        gsrs_hierarchy,
        gsrs_names,
        gsrs_search,
        gsrs_structure,
        gsrs_structure_search,
        gsrs_substance,
        gsrs_unii_from_name,
        gsrs_vocabularies,
    )

    cmd = args.command
    if cmd == "search":
        result = gsrs_search(args.query, top=args.top, skip=args.skip)
    elif cmd == "substance":
        result = gsrs_substance(args.unii)
    elif cmd == "names":
        result = gsrs_names(args.unii)
    elif cmd == "codes":
        result = gsrs_codes(args.unii)
    elif cmd == "structure":
        result = gsrs_structure(args.unii)
    elif cmd == "structure-search":
        result = gsrs_structure_search(
            args.smiles,
            search_type=args.search_type,
            cutoff=args.cutoff,
            top=args.top,
        )
    elif cmd == "hierarchy":
        result = gsrs_hierarchy(args.unii)
    elif cmd == "browse":
        result = gsrs_browse(top=args.top, skip=args.skip)
    elif cmd == "vocabularies":
        result = gsrs_vocabularies()
    elif cmd == "unii-from-name":
        result = gsrs_unii_from_name(args.name, top=args.top)
    elif cmd == "all":
        result = gsrs_all(args.unii)
    else:
        parser.print_help()
        sys.exit(1)

    _print(result, fmt)


if __name__ == "__main__":
    main()
