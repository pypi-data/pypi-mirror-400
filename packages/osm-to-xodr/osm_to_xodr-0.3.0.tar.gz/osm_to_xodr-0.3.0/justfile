# OSM to OpenDRIVE Converter - Task Runner
# Usage: just <recipe>
# Run `just` or `just --list` to see all available commands

set shell := ["bash", "-c"]

# Default recipe shows help
default:
    @just --list

# List available commands
help:
    @just --list

# === Setup ===

# Install dependencies and set up the environment
install:
    uv sync --all-groups

# Clean all build artifacts and caches
clean:
    rm -rf dist/ build/ *.egg-info .pytest_cache .coverage htmlcov/ coverage.xml
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true

# === Development ===

# Run linters (pre-commit hooks)
lint:
    uv run pre-commit run --all-files --show-diff-on-failure

# Format code
fmt:
    uv run ruff format .
    uv run ruff check --fix .

# Run all tests
test:
    uv run pytest -m "not integration"

# Run tests with coverage
test-cov:
    uv run pytest -m "not integration" --cov=src/osm_to_xodr --cov-report=html --cov-report=term

# Run integration tests (requires SUMO netconvert installed)
test-integration:
    uv run pytest -m integration -v

# === Build & Verify ===

# Build the package (sdist and wheel)
build:
    uv build

# Verify the package contents
verify:
    @echo "Checking wheel contents..."
    @unzip -l dist/*.whl | head -30
    @echo ""
    @echo "Checking sdist contents..."
    @tar -tzf dist/*.tar.gz | head -30

# Test installation in a fresh environment
test-install:
    @echo "Testing installation from wheel..."
    uv run --isolated --with dist/*.whl -- osm-to-xodr --help

# === CLI Commands ===

# Check netconvert availability
check:
    uv run osm-to-xodr check

# Generate example .env configuration
init-config:
    uv run osm-to-xodr init-config

# Convert a sample OSM file (ekas.osm)
convert-test:
    mkdir -p output
    uv run osm-to-xodr convert tests/data/ekas.osm -o output/ekas_test.xodr -v

# Convert any OSM file: just convert <input.osm> [output.xodr]
convert input output="output/$(basename {{input}} .osm).xodr":
    mkdir -p $(dirname {{output}})
    uv run osm-to-xodr convert {{input}} -o {{output}}

# === CI ===

# Run pre-commit hooks and tests (like immich-migrator check)
check-all: lint test
    @echo "✅ All checks passed!"

# Run the full release pipeline locally
all: clean install check-all build verify test-install
    @echo "✅ Full pipeline completed!"
