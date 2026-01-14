"""Tests for the config module."""

from __future__ import annotations

from osm_to_xodr.config import (
    AppSettings,
    NetconvertSettings,
    generate_env_template,
)


def test_netconvert_settings_defaults() -> None:
    """Test that NetconvertSettings has expected defaults."""
    settings = NetconvertSettings()

    assert settings.lane_width == 3.5
    assert settings.sidewalk_width == 2.0
    assert settings.bikelane_width == 1.5
    assert settings.crossing_width == 4.0
    assert settings.shape_match_dist == 10.0
    assert settings.junction_corner_detail == 5
    assert settings.guess_roundabouts is True
    assert settings.guess_ramps is True
    assert settings.import_sidewalks is True
    assert settings.no_turnarounds is True


def test_app_settings_defaults() -> None:
    """Test that AppSettings has expected defaults."""
    settings = AppSettings()

    assert settings.output_dir.name == "output"
    assert settings.tmp_dir.name == "tmp"
    assert settings.keep_intermediate is False
    assert settings.verbose is False
    assert settings.timeout == 300


def test_generate_env_template() -> None:
    """Test that env template generation works."""
    template = generate_env_template()

    assert "OSM_TO_XODR_LANE_WIDTH" in template
    assert "OSM_TO_XODR_VERBOSE" in template
    assert "OSM_TO_XODR_OUTPUT_DIR" in template
    assert template.startswith("# OSM to OpenDRIVE")
