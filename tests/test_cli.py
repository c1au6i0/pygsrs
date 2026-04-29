"""Tests for the CLI."""
import pytest
from conftest import ASPIRIN_UNII, BASE, NAMES_LIST, SUBSTANCE_FULL, SUBSTANCES_ENVELOPE

from pygsrs._cli import main


def test_cli_search_table(httpx_mock, capsys):
    httpx_mock.add_response(
        url=f"{BASE}/substances/search?q=aspirin&top=10&skip=0",
        json=SUBSTANCES_ENVELOPE,
    )
    main(["search", "aspirin"])
    out = capsys.readouterr().out
    assert "ASPIRIN" in out or "R16CO5Y76E" in out


def test_cli_search_csv(httpx_mock, capsys):
    httpx_mock.add_response(
        url=f"{BASE}/substances/search?q=aspirin&top=10&skip=0",
        json=SUBSTANCES_ENVELOPE,
    )
    main(["search", "aspirin", "--format", "csv"])
    out = capsys.readouterr().out
    assert "approval_id" in out


def test_cli_search_json(httpx_mock, capsys):
    httpx_mock.add_response(
        url=f"{BASE}/substances/search?q=aspirin&top=10&skip=0",
        json=SUBSTANCES_ENVELOPE,
    )
    main(["search", "aspirin", "--format", "json"])
    out = capsys.readouterr().out
    assert '"approval_id"' in out


def test_cli_names(httpx_mock, capsys):
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})/names",
        json=NAMES_LIST,
    )
    main(["names", ASPIRIN_UNII])
    out = capsys.readouterr().out
    assert "ASPIRIN" in out


def test_cli_no_results_exits_nonzero():
    """Empty query is rejected by validation before any HTTP call."""
    with pytest.raises(SystemExit) as exc:
        main(["search", ""])
    assert exc.value.code != 0


def test_cli_structure_from_id_by_unii(httpx_mock, capsys):
    """structure-from-id with a UNII goes direct to structure endpoint."""
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})",
        json=SUBSTANCE_FULL,
    )
    main(["structure-from-id", ASPIRIN_UNII])
    out = capsys.readouterr().out
    assert "smiles" in out or "C9H8O4" in out


def test_cli_structure_from_id_by_name(httpx_mock, capsys):
    """structure-from-id with a name resolves via name search then fetches structure."""
    httpx_mock.add_response(
        url=f"{BASE}/substances/search?q=root_names_name%3A%22ASPIRIN%22&top=1",
        json=SUBSTANCES_ENVELOPE,
    )
    httpx_mock.add_response(
        url=f"{BASE}/substances({ASPIRIN_UNII})",
        json=SUBSTANCE_FULL,
    )
    main(["structure-from-id", "ASPIRIN", "--id-type", "name"])
    out = capsys.readouterr().out
    assert "smiles" in out or "C9H8O4" in out


def test_cli_structure_from_id_no_match_exits_nonzero(httpx_mock):
    """structure-from-id exits with non-zero code when identifier cannot be resolved."""
    httpx_mock.add_response(
        url=f"{BASE}/substances/search?q=root_names_name%3A%22NOTASUBSTANCE%22&top=1",
        json={"content": [], "total": 0, "count": 0, "skip": 0},
    )
    with pytest.raises(SystemExit) as exc:
        main(["structure-from-id", "NOTASUBSTANCE", "--id-type", "name"])
    assert exc.value.code != 0
