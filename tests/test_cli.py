"""Tests for the CLI."""
import pytest
from conftest import ASPIRIN_UNII, BASE, NAMES_LIST, SUBSTANCES_ENVELOPE

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
