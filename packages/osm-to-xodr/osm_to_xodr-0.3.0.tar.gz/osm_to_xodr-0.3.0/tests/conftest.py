"""Test configuration and fixtures."""

from __future__ import annotations

import shutil
from collections.abc import Generator
from pathlib import Path

import pytest


@pytest.fixture
def data_dir() -> Path:
    """Return path to the data directory."""
    return Path(__file__).parent.parent / "data"


@pytest.fixture
def osm_dir(data_dir: Path) -> Path:
    """Return path to OSM input files."""
    return data_dir / "osm"


@pytest.fixture(params=["ekas.osm", "hulta.osm"])
def sample_osm_file(request) -> Path:
    """Return path to an OSM sample file (parametrized)."""
    return Path(__file__).parent / "data" / request.param


@pytest.fixture
def tmp_output_dir() -> Generator[Path, None, None]:
    """Return a temporary output directory.

    For Flatpak compatibility, we use a directory within the project
    rather than system /tmp when running integration tests.
    """
    # Check if we should use project-local temp dir for Flatpak
    # Flatpak can't access /tmp directories
    project_root = Path(__file__).parent.parent
    output_dir = project_root / "tmp" / "test_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    yield output_dir
    # Cleanup after test
    shutil.rmtree(output_dir, ignore_errors=True)
