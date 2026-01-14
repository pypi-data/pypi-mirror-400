"""Integration tests for the full conversion pipeline."""

from __future__ import annotations

from pathlib import Path

import pytest

from osm_to_xodr.converter import convert_osm_to_xodr
from osm_to_xodr.netconvert import check_netconvert_available


@pytest.mark.integration
@pytest.mark.skipif(
    not check_netconvert_available(),
    reason="netconvert not available",
)
def test_convert_osm_file(sample_osm_file: Path, tmp_output_dir: Path) -> None:
    """Test converting OSM sample files to XODR."""
    output_file = tmp_output_dir / f"{sample_osm_file.stem}.xodr"

    result = convert_osm_to_xodr(
        sample_osm_file,
        output_file,
        verbose=True,
    )

    assert result.success, f"Conversion failed: {result.error}"
    assert result.output_file is not None
    assert result.output_file.exists()
    assert result.output_file.stat().st_size > 0

    # Verify it's valid XML
    content = result.output_file.read_text()
    assert "<OpenDRIVE" in content
    assert "</OpenDRIVE>" in content
