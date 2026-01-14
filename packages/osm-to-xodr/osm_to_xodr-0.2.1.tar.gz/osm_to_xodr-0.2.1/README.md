# 🗺️ osm-to-xodr

[![uv][uv-badge]][uv]
[![PyPI][pypi-badge]][pypi]
[![Python Version][python-badge]][pypi]
[![Tests][tests-badge]][tests]
[![License][license-badge]][license]

[uv]: https://github.com/astral-sh/uv
[uv-badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json
[pypi-badge]: https://img.shields.io/pypi/v/osm-to-xodr
[pypi]: https://pypi.org/project/osm-to-xodr/
[python-badge]: https://img.shields.io/pypi/pyversions/osm-to-xodr
[tests-badge]: https://github.com/RISE-Dependable-Transport-Systems/osm-to-xodr/actions/workflows/test.yaml/badge.svg
[tests]: https://github.com/RISE-Dependable-Transport-Systems/osm-to-xodr/actions/workflows/test.yaml
[license-badge]: https://img.shields.io/github/license/RISE-Dependable-Transport-Systems/osm-to-xodr
[license]: ./LICENSE

Convert OpenStreetMap (`.osm`) files to OpenDRIVE (`.xodr`) using SUMO's `netconvert` with optimized defaults for driving simulators like CARLA.

---

## ✨ Features

- 🎯 **Sane Defaults**: Pre-configured netconvert parameters optimized for realistic road networks
- 🚦 **Traffic Sign Support**: Extracts and converts traffic signs to OpenDRIVE signals
- ⚙️ **Highly Configurable**: Settings via CLI arguments, environment variables, or `.env` file
- 🎨 **Modern Python CLI**: Built with Typer, Rich progress display, and Loguru logging
- 🧩 **Modular Architecture**: Clean separation of concerns for easy maintenance

---

## 📋 Requirements

- **Python**: 3.11 or higher ✅
- **SUMO**: For `netconvert` command 🚗

### Installing SUMO

> [!IMPORTANT]
> SUMO's `netconvert` is required for conversion. Choose your installation method below:

**Linux (Ubuntu/Debian):**

```bash
# Stable release
sudo add-apt-repository ppa:sumo/stable
sudo apt-get update
sudo apt-get install sumo sumo-tools

# Or via Flatpak
flatpak install flathub org.eclipse.sumo
```

**macOS / Linux:**

```bash
brew tap dlr-ts/sumo
brew install sumo
```

**Windows:**

Download from [SUMO Downloads](https://sumo.dlr.de/docs/Downloads.html)

## 📦 Installation

> [!TIP]
> Use **uvx** to run the tool instantly without installation — perfect for quick conversions:
>
> ```bash
> uvx osm-to-xodr convert map.osm
> ```

### Install from PyPI

```bash
# With uv (recommended)
uv tool install osm-to-xodr

# Or with pip
pip install osm-to-xodr
```

### From Source

```bash
git clone https://github.com/RISE-Dependable-Transport-Systems/osm-to-xodr.git
cd osm-to-xodr
uv sync
```

## 🚀 Quick Start

### 1. Verify SUMO Installation

> [!NOTE]
> This command checks if `netconvert` is available and shows version information.

```bash
osm-to-xodr check
```

### 2. Convert Your First Map

```bash
# Basic conversion with optimized defaults
osm-to-xodr convert map.osm

# Custom output location
osm-to-xodr convert map.osm -o output/my_network.xodr

# Enable verbose logging
osm-to-xodr convert map.osm -v
```

### 3. (Optional) Generate Configuration Template

```bash
osm-to-xodr init-config
```

This creates a `.env` file with all available settings for customization.

## CLI Reference

### `osm-to-xodr convert`

Convert an OpenStreetMap file to OpenDRIVE format.

```text
Usage: osm-to-xodr convert [OPTIONS] INPUT_FILE

Arguments:
  INPUT_FILE  Input OpenStreetMap (.osm) file

Options:
  -o, --output PATH              Output OpenDRIVE (.xodr) file
  -d, --output-dir PATH          Output directory [default: output]

  --lane-width FLOAT             Default lane width in meters [default: 3.5]
  --sidewalk-width FLOAT         Default sidewalk width [default: 2.0]
  --bikelane-width FLOAT         Default bike lane width [default: 1.5]
  --crossing-width FLOAT         Default crossing width [default: 4.0]

  --no-roundabouts               Disable roundabout guessing
  --no-ramps                     Disable ramp guessing
  --no-tls                       Disable traffic light guessing
  --no-sidewalks                 Don't import sidewalks
  --no-crossings                 Don't import crossings
  --no-turn-lanes                Don't import turn lanes
  --no-bike-access               Don't import bike access
  --keep-geometry                Don't simplify geometry
  --turnarounds                  Enable turnaround connections

  -k, --keep-intermediate        Keep intermediate files
  -v, --verbose                  Enable verbose output
  -V, --version                  Show version
```

### `osm-to-xodr check`

Check if netconvert is available and show version information.

### `osm-to-xodr init-config`

Generate a template `.env` configuration file with all available settings.

## ⚙️ Configuration

Settings can be configured via:

1. **CLI arguments** (highest priority)
2. **Environment variables** with `OSM_TO_XODR_` prefix
3. **`.env` file** in the current directory

> [!TIP]
> CLI flags take precedence over environment variables and `.env` file settings.

### Environment Variables

```bash
# Lane dimensions
OSM_TO_XODR_LANE_WIDTH=3.5
OSM_TO_XODR_SIDEWALK_WIDTH=2.0
OSM_TO_XODR_BIKELANE_WIDTH=1.5
OSM_TO_XODR_CROSSING_WIDTH=4.0

# Feature flags
OSM_TO_XODR_GUESS_ROUNDABOUTS=true
OSM_TO_XODR_GUESS_RAMPS=true
OSM_TO_XODR_GUESS_TLS_SIGNALS=true
OSM_TO_XODR_IMPORT_SIDEWALKS=true
OSM_TO_XODR_IMPORT_CROSSINGS=true
OSM_TO_XODR_IMPORT_TURN_LANES=true
OSM_TO_XODR_IMPORT_BIKE_ACCESS=true
OSM_TO_XODR_REMOVE_GEOMETRY=true
OSM_TO_XODR_NO_TURNAROUNDS=true

# Application settings
OSM_TO_XODR_OUTPUT_DIR=output
OSM_TO_XODR_TMP_DIR=tmp
OSM_TO_XODR_KEEP_INTERMEDIATE=false
OSM_TO_XODR_VERBOSE=false
```

## 📁 Project Structure

```text
osm-to-xodr/
├── src/osm_to_xodr/
│   ├── __init__.py      # Package metadata
│   ├── cli.py           # Typer CLI interface
│   ├── config.py        # Pydantic settings
│   ├── converter.py     # Main orchestration
│   ├── netconvert.py    # SUMO subprocess wrapper
│   └── postprocess.py   # Signal conversion
├── data/
│   ├── osm/             # Input OSM files
│   └── xodr/            # Output XODR files
├── tests/               # Pytest test suite
├── justfile             # Task runner
└── pyproject.toml       # Project configuration
```

## 🛠️ Development

### Setup

```bash
# Clone repository
git clone https://github.com/RISE-Dependable-Transport-Systems/osm-to-xodr.git
cd osm-to-xodr

# Install with dev dependencies
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install
```

### Task Runner (just)

```bash
# Show available commands
just

# Run linting
just lint

# Run tests
just test

# Run tests with coverage
just test-cov

# Format code
just fmt

# Run pre-commit on all files
just pre-commit

# Test conversion with sample file
just convert-test

# Full CI pipeline
just ci
```

### Running Tests

```bash
# Run all tests
just test

# Run unit tests only
uv run pytest -m "not integration"

# Run integration tests (requires netconvert)
uv run pytest -m integration

# With coverage
uv run pytest --cov=osm_to_xodr --cov-report=html
```

> [!NOTE]
> Integration tests require SUMO's `netconvert` to be installed and available in your PATH.

## 🔧 Troubleshooting

### ❌ netconvert Not Found

> [!WARNING]
> If you see `netconvert not found` errors:
>
> - ✅ Verify SUMO is installed: `netconvert --version`
> - ✅ Check that SUMO's `bin` directory is in your PATH
> - ✅ On Linux, ensure you installed `sumo` not just `sumo-tools`

### 🗺️ Conversion Errors

> [!TIP]
> If conversion fails:
>
> - Use `--verbose` flag to see detailed netconvert output
> - Check your OSM file is valid (open in JOSM or similar)
> - Try with `--keep-intermediate` to inspect intermediate `.net.xml` files
> - Reduce map complexity by focusing on smaller areas

### ⚠️ Missing Road Features

> [!NOTE]
> If converted roads are missing expected features:
>
> - Ensure your OSM data has proper road tags (check on OpenStreetMap.org)
> - Some features require specific flags (e.g., `--no-sidewalks` disables sidewalk import)
> - Use `--keep-geometry` to prevent road geometry simplification

---

## 🔍 How It Works

The conversion process has three steps:

1. **Extract Traffic Signs**: First netconvert pass extracts traffic sign POIs from OSM
2. **Generate OpenDRIVE**: Second pass creates the road network with signs as objects
3. **Post-process Signals**: Python converts `<object>` elements to proper `<signal>` elements for CARLA compatibility

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 🙌 Credits

- [SUMO](https://www.eclipse.org/sumo/) - Simulation of Urban Mobility
- [OpenDRIVE](https://www.asam.net/standards/detail/opendrive/) - ASAM OpenDRIVE standard
