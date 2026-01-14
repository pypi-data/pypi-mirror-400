"""Integration tests validating geometry accuracy against OSM source."""

import math
import statistics
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import pytest
import utm

from osm_to_xodr.converter import convert_osm_to_xodr


@dataclass
class Point:
    x: float
    y: float
    id: str = ""
    junction: str = "-1"


def parse_osm_nodes(osm_file: Path) -> list[Point]:
    """Parse OSM nodes and convert to UTM."""
    tree = ET.parse(osm_file)
    root = tree.getroot()

    nodes_utm = []

    for node in root.findall("node"):
        lat_str = node.get("lat")
        lon_str = node.get("lon")
        node_id = node.get("id", "")

        if lat_str and lon_str:
            lat = float(lat_str)
            lon = float(lon_str)
            easting, northing, _, _ = utm.from_latlon(lat, lon)
            nodes_utm.append(Point(easting, northing, node_id))

    return nodes_utm


def parse_xodr_geometry(xodr_file: Path) -> list[Point]:
    """Parse XODR road start points and apply header offset."""
    tree = ET.parse(xodr_file)
    root = tree.getroot()

    header = root.find("header")
    if header is None:
        return []

    offset = header.find("offset")

    # Defaults
    off_x = 0.0
    off_y = 0.0

    if offset is not None:
        off_x = float(offset.get("x", 0))
        off_y = float(offset.get("y", 0))

    road_points = []

    for road in root.findall("road"):
        plan_view = road.find("planView")
        if plan_view is None:
            continue

        # Get the first geometry element (start of road)
        geo = plan_view.find("geometry")
        if geo is not None:
            local_x = float(geo.get("x", 0))
            local_y = float(geo.get("y", 0))

            # Convert to World UTM
            world_x = local_x + off_x
            world_y = local_y + off_y

            road_points.append(
                Point(world_x, world_y, road.get("id", ""), road.get("junction", "-1"))
            )

    return road_points


def find_nearest_match(target: Point, cloud: list[Point]) -> tuple[float, Point | None]:
    """Find the nearest point in cloud."""
    min_dist_sq = float("inf")
    nearest_p = None

    for p in cloud:
        dx = target.x - p.x
        dy = target.y - p.y
        dist_sq = dx * dx + dy * dy
        if dist_sq < min_dist_sq:
            min_dist_sq = dist_sq
            nearest_p = p

    return math.sqrt(min_dist_sq), nearest_p


@pytest.mark.integration
def test_geometry_accuracy_osm(sample_osm_file, tmp_path):
    """Verify that generated XODR geometry aligns with OSM source nodes."""
    osm_path = sample_osm_file

    # Flatpak workaround: Use a directory in the workspace, not /tmp
    # because Flatpak might not have access to pytest's /tmp dir
    project_root = Path(__file__).parent.parent
    workspace_tmp = project_root / "output/test_tmp_acc"
    workspace_tmp.mkdir(parents=True, exist_ok=True)

    # Use a unique name to avoid conflicts
    xodr_path = workspace_tmp / f"{osm_path.stem}_accuracy.xodr"

    if not osm_path.exists():
        pytest.skip(f"OSM source file missing: {osm_path}")

    # Run conversion
    result = convert_osm_to_xodr(osm_path, xodr_path)
    assert result.success, f"Conversion failed: {result.error}"
    assert xodr_path.exists()

    # Parse Geometries
    osm_points = parse_osm_nodes(osm_path)
    xodr_points = parse_xodr_geometry(xodr_path)

    assert len(osm_points) > 0, "Failed to parse OSM nodes"
    assert len(xodr_points) > 0, "Failed to parse XODR geometries"

    # Match Points
    matches = []
    for rp in xodr_points:
        dist, osm_p = find_nearest_match(rp, osm_points)

        # We expect SOME points to match reasonably well.
        # Filter for points that are likely the "same" point (within 20m)
        if dist < 20.0:
            matches.append(
                {
                    "dist": dist,
                    "xodr_id": rp.id,
                    "osm_id": osm_p.id if osm_p else "None",
                }
            )

    # Assertions

    # 1. We should find matches for a majority of roads (sanity check)
    # The ekas map produces about 94 starts. We expect most to key off OSM nodes.
    assert len(matches) > 10, f"Too few geometric matches found ({len(matches)})"

    distances = [m["dist"] for m in matches]
    mean_error = statistics.mean(distances)
    median_error = statistics.median(distances)
    max_error = max(distances)

    print(f"\nStats: Mean={mean_error:.2f}m, Median={median_error:.2f}m, Max={max_error:.2f}m")

    # 2. Mean error should be reasonable.
    # From manual verification we know it's ~3.7m due to netconvert smoothing.
    # Allowing up to 10m to account for updates/different Netconvert versions.
    # If it's > 10m, something might be fundamentally wrong with offset/projection.
    assert mean_error < 10.0, f"Mean error {mean_error}m is suspiciously high (drift?)"

    # 3. Check that we have at least ONE high-precision match
    # (Matches < 0.1m indicate the projection system is aligned, even if geometry drifts)
    min_error = min(distances)
    assert min_error < 0.1, f"No high precision matches found. Best was {min_error}m"
