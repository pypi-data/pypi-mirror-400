# Netconvert (SUMO)

## What is netconvert?

`netconvert` is a system binary from SUMO (Simulation of Urban MObility). It's NOT a Python package—we wrap it using `subprocess.run()`.

## Installation

- **Linux**: `apt install sumo sumo-tools` or Flatpak
- **macOS**: `brew tap dlr-ts/sumo && brew install sumo`
- **CI**: GitHub Actions installs via apt

The code auto-detects system install vs Flatpak in `netconvert.py:find_netconvert()`.

## Parameter Categories

The ~40 netconvert parameters in `netconvert.py:generate_opendrive()`:

- **Geometry**: `--geometry.remove`, `--geometry.min-dist`
- **Junctions**: `--roundabouts.guess`, `--junctions.corner-detail`
- **OSM Import**: `--osm.sidewalks`, `--osm.turn-lanes`, `--osm.crossings`
- **Defaults**: `--default.lanewidth`, `--default.sidewalk-width`

## Adding a New Parameter

1. Add parameter to `netconvert.py:generate_opendrive()` function signature
2. Add to args list in the function body
3. Add corresponding setting in `config.py:NetconvertSettings`
4. Add CLI option in `cli.py:convert()` command
5. Update `.env` template in `config.py:generate_env_template()`

## External Documentation

- SUMO netconvert docs: <https://sumo.dlr.de/docs/netconvert.html>
- OpenDRIVE spec: <https://www.asam.net/standards/detail/opendrive/>
- CARLA OpenDRIVE: <https://carla.readthedocs.io/en/latest/core_map/>
