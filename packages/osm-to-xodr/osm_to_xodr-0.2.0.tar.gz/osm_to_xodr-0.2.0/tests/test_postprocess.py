"""Tests for the postprocess module."""

from __future__ import annotations

import tempfile
from pathlib import Path

from osm_to_xodr.postprocess import (
    TYPE_MAPPING,
    convert_objects_to_signals,
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
