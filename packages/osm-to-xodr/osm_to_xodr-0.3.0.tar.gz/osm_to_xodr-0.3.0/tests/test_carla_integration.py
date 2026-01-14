import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
import utm

from osm_to_xodr.converter import convert_osm_to_xodr

# Try to import carla
try:
    import carla
except ImportError:
    carla = None


@pytest.mark.skipif(carla is None, reason="carla package not installed")
def verify_xodr_with_carla(
    xodr_path: Path, expected_lat: float, expected_lon: float
) -> tuple[bool, str, float, float]:
    """Verify XODR file loaded in CARLA matches expected coordinates.

    Returns:
        tuple (success, message, actual_lat, actual_lon)
    """
    if not xodr_path.exists():
        return False, f"File not found: {xodr_path}", 0.0, 0.0

    try:
        with open(xodr_path) as f:
            content = f.read()

        # Load map from memory
        carla_map = carla.Map("test_map", content)

        # Transform (0,0,0) - map origin - to GeoLocation
        origin = carla.Location(0, 0, 0)
        geo = carla_map.transform_to_geolocation(origin)

        # Check tolerance (high precision expected now)
        lat_diff = abs(geo.latitude - expected_lat)
        lon_diff = abs(geo.longitude - expected_lon)

        # Tolerance: 1e-5 degrees is approx 1 meter.
        # utm conversion might have minor precision diffs, so keep 1e-4 (~10m) safety
        matches = lat_diff < 0.0001 and lon_diff < 0.0001

        msg = f"Lat: {geo.latitude} (exp {expected_lat}), Lon: {geo.longitude} (exp {expected_lon})"
        return matches, msg, geo.latitude, geo.longitude

    except Exception as e:
        return False, f"CARLA parsing exception: {e}", 0.0, 0.0


@pytest.mark.skipif(carla is None, reason="carla package not installed")
@pytest.mark.integration
def test_carla_georeference_fix(sample_osm_file, tmp_path):
    """Verify that newly generated maps work with CARLA georeferencing,
    validating that the Origin (0,0,0) matches the UTM offset."""

    # Setup paths
    osm_path = sample_osm_file

    project_root = Path(__file__).parent.parent
    workspace_tmp = project_root / "output/test_tmp"
    workspace_tmp.mkdir(parents=True, exist_ok=True)
    new_xodr_path = workspace_tmp / f"{osm_path.stem}_fixed.xodr"

    if not osm_path.exists():
        pytest.skip(f"OSM source file missing: {osm_path}")

    # 1. Convert Fresh (Positive Test)
    result = convert_osm_to_xodr(osm_path, new_xodr_path)
    assert result.success, f"Conversion failed: {result.error}"
    assert new_xodr_path.exists()

    # 2. Extract Offset and Zone from Generated File
    # We trust that our code put the calculated lat/lon in based on THIS offset.
    # So we verify that CARLA agrees with our calculation.
    tree = ET.parse(new_xodr_path)
    root = tree.getroot()

    header = root.find("header")
    offset = header.find("offset")
    x = float(offset.get("x", 0))
    y = float(offset.get("y", 0))

    georef = header.find("geoReference").text
    zone_match = re.search(r"\+zone=(\d+)", georef)
    assert zone_match, "No UTM zone found in output"
    zone = int(zone_match.group(1))

    # Check hemisphere (Sweden is North)
    northern = "+south" not in georef

    # Calculate Expected Origin Lat/Lon
    expected_lat, expected_lon = utm.to_latlon(x, y, zone, northern=northern)

    # 3. Verify with CARLA
    # This proves:
    # a) We wrote +lat_0/+lon_0 into the file correctly
    # b) CARLA read them and uses them as the origin
    success, msg, lat, lon = verify_xodr_with_carla(new_xodr_path, expected_lat, expected_lon)
    print(f"\nVerification result: {msg}")

    assert success, f"New XODR failed CARLA georeference check: {msg}"


@pytest.mark.skipif(carla is None, reason="carla package not installed")
@pytest.mark.integration
def test_carla_map_content_validity(sample_osm_file, tmp_path):
    """Verify that the generated XODR loads into CARLA with valid topology and waypoints."""

    # Reuse the same conversion (or rely on fixture if refactored, but simple call is fine)
    osm_path = sample_osm_file

    project_root = Path(__file__).parent.parent
    workspace_tmp = project_root / "output/test_tmp"
    workspace_tmp.mkdir(parents=True, exist_ok=True)
    xodr_path = workspace_tmp / f"{osm_path.stem}_fixed.xodr"

    if not xodr_path.exists():
        # Only run conversion if previous test didn't (or separate isolation)
        if not osm_path.exists():
            pytest.skip(f"OSM source file missing: {osm_path}")
        result = convert_osm_to_xodr(osm_path, xodr_path)
        assert result.success

    with open(xodr_path) as f:
        content = f.read()

    # Load map
    carla_map = carla.Map("test_content_map", content)

    # 1. Check Topology
    topology = carla_map.get_topology()
    # Expect at least some edges for the map
    assert len(topology) > 0, "Map loaded but has no topology edges"
    print(f"Topology edges: {len(topology)}")

    # 2. Check Waypoints
    waypoints = carla_map.generate_waypoints(distance=5.0)
    assert len(waypoints) > 0, "Map loaded but could not generate waypoints"
    print(f"Generated {len(waypoints)} waypoints")

    # 3. Check for obvious errors (optional, usually load raises)
