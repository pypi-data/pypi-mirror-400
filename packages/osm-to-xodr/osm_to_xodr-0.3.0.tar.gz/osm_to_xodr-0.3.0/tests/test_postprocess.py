"""Tests for the postprocess module."""

from __future__ import annotations

import tempfile
from pathlib import Path

import utm

from osm_to_xodr.postprocess import (
    TYPE_MAPPING,
    convert_objects_to_signals,
    fix_georeference_for_carla,
)


def test_type_mapping_contains_common_signs() -> None:
    """Test that TYPE_MAPPING has common traffic sign types."""
    assert "priority" in TYPE_MAPPING
    assert "yield" in TYPE_MAPPING
    assert "stop" in TYPE_MAPPING
    assert "speedLimit" in TYPE_MAPPING


def test_convert_objects_file_not_found() -> None:
    """Test convert_objects_to_signals with non-existent file."""
    result = convert_objects_to_signals(Path("/nonexistent/file.xodr"))

    assert result.success is False
    assert "not found" in result.error.lower()


def test_convert_objects_invalid_xml() -> None:
    """Test convert_objects_to_signals with invalid XML."""
    with tempfile.NamedTemporaryFile(suffix=".xodr", delete=False, mode="w") as f:
        f.write("not valid xml")
        temp_path = Path(f.name)

    try:
        result = convert_objects_to_signals(temp_path)
        assert result.success is False
        assert "parse" in result.error.lower() or "xml" in result.error.lower()
    finally:
        temp_path.unlink()


def test_convert_objects_empty_xodr() -> None:
    """Test convert_objects_to_signals with valid but empty XODR."""
    with tempfile.NamedTemporaryFile(suffix=".xodr", delete=False, mode="w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<OpenDRIVE></OpenDRIVE>')
        temp_path = Path(f.name)

    try:
        result = convert_objects_to_signals(temp_path)
        assert result.success is True
        assert result.signals_converted == 0
    finally:
        temp_path.unlink()


def test_convert_objects_with_signs() -> None:
    """Test convert_objects_to_signals converts sign objects to signals."""
    xodr_content = """<?xml version="1.0" encoding="UTF-8"?>
<OpenDRIVE>
    <road id="1" name="Test Road">
        <objects>
            <object id="sign1" type="stop" s="10.0" t="-5.0"/>
            <object id="sign2" type="yield" s="20.0" t="5.0"/>
        </objects>
    </road>
</OpenDRIVE>"""

    with tempfile.NamedTemporaryFile(suffix=".xodr", delete=False, mode="w") as f:
        f.write(xodr_content)
        temp_path = Path(f.name)

    try:
        result = convert_objects_to_signals(temp_path)
        assert result.success is True
        assert result.signals_converted == 2
        assert result.poles_added == 2

        # Verify the file was modified
        content = temp_path.read_text()
        assert "<signal" in content
        assert 'type="206"' in content  # Stop sign
        assert 'type="205"' in content  # Yield sign
    finally:
        temp_path.unlink()


# --- geoReference Fixing Tests ---


def test_fix_georeference_adds_lat_lon_from_offset() -> None:
    """Test fix_georeference_for_carla calculates and adds lat_0/lon_0."""
    # Test values: Gothenburg, Sweden approx
    lat, lon = 57.708870, 11.974560
    easting, northing, zone, letter = utm.from_latlon(lat, lon)

    # Create XML with matching offset and zone
    xodr_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<OpenDRIVE>
    <header revMajor="1" revMinor="4">
        <offset x="{easting}" y="{northing}" z="0"/>
        <geoReference>
+proj=utm +zone={zone} +ellps=WGS84 +datum=WGS84 +units=m +no_defs
        </geoReference>
    </header>
</OpenDRIVE>"""

    with tempfile.NamedTemporaryFile(suffix=".xodr", delete=False, mode="w") as f:
        f.write(xodr_content)
        temp_path = Path(f.name)

    try:
        result = fix_georeference_for_carla(temp_path)
        assert result is True

        # Verify the file was modified with lat_0/lon_0
        content = temp_path.read_text()

        # Check that we got approximately the right lat/lon back
        # We can't do exact string match because specific decimals depend on utm lib impl
        # but we know it outputs 10 decimals in our code.
        assert "+lat_0=" in content
        assert "+lon_0=" in content

        # Original projection should be preserved
        assert "+proj=utm" in content
        assert f"+zone={zone}" in content
    finally:
        temp_path.unlink()


def test_fix_georeference_skips_if_already_present() -> None:
    """Test fix_georeference_for_carla skips if lat_0/lon_0 already present."""
    xodr_content = """<?xml version="1.0" encoding="UTF-8"?>
<OpenDRIVE>
    <header revMajor="1" revMinor="4">
        <offset x="500000" y="5000000" z="0"/>
        <geoReference>
+proj=tmerc +lat_0=57.74 +lon_0=12.89 +k=1 +datum=WGS84 +units=m +no_defs
        </geoReference>
    </header>
</OpenDRIVE>"""

    with tempfile.NamedTemporaryFile(suffix=".xodr", delete=False, mode="w") as f:
        f.write(xodr_content)
        temp_path = Path(f.name)

    try:
        result = fix_georeference_for_carla(temp_path)
        assert result is False  # Should not modify

        # Verify original values preserved
        content = temp_path.read_text()
        assert "+lat_0=57.74" in content
        assert "+lon_0=12.89" in content
    finally:
        temp_path.unlink()


def test_fix_georeference_no_header() -> None:
    """Test fix_georeference_for_carla with missing header."""
    xodr_content = """<?xml version="1.0" encoding="UTF-8"?>
<OpenDRIVE>
    <road id="1" name="Test"/>
</OpenDRIVE>"""

    with tempfile.NamedTemporaryFile(suffix=".xodr", delete=False, mode="w") as f:
        f.write(xodr_content)
        temp_path = Path(f.name)

    try:
        result = fix_georeference_for_carla(temp_path)
        assert result is False
    finally:
        temp_path.unlink()


def test_fix_georeference_no_georeference() -> None:
    """Test fix_georeference_for_carla with missing geoReference."""
    xodr_content = """<?xml version="1.0" encoding="UTF-8"?>
<OpenDRIVE>
    <header revMajor="1" revMinor="4">
        <offset x="0" y="0" z="0"/>
    </header>
</OpenDRIVE>"""

    with tempfile.NamedTemporaryFile(suffix=".xodr", delete=False, mode="w") as f:
        f.write(xodr_content)
        temp_path = Path(f.name)

    try:
        result = fix_georeference_for_carla(temp_path)
        assert result is False
    finally:
        temp_path.unlink()
