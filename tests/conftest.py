"""Shared pytest fixtures and helpers."""
import time
import pytest


# Aspirin reference constants
ASPIRIN_UNII = "R16CO5Y76E"
ASPIRIN_SMILES = "CC(=O)Oc1ccccc1C(=O)O"
ASPIRIN_NAME = "ASPIRIN"

NICOTINE_UNII = "6M3C89ZY6R"
NICOTINE_NAME = "NICOTINE"


@pytest.fixture(autouse=True)
def rate_limit():
    """Sleep between every test to avoid hammering the API."""
    yield
    time.sleep(1)
