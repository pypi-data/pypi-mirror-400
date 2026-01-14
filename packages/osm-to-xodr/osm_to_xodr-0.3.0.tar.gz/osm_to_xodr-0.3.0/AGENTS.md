# AGENTS.md

## What This Is

**osm-to-xodr**: Converts OpenStreetMap (`.osm`) → OpenDRIVE (`.xodr`) for driving simulators (CARLA).

Uses SUMO's `netconvert` binary (system dependency, not Python) via `subprocess.run()`.

## Quick Start

```bash
uv sync --all-extras          # Install dependencies
just lint && just test        # Validate changes
just convert-test             # Full conversion test with ekas.osm
```

## Project Structure

```text
src/osm_to_xodr/
├── cli.py           # Typer CLI
├── config.py        # Pydantic settings
├── converter.py     # Orchestrates conversion
├── netconvert.py    # SUMO netconvert wrapper (parameters here)
└── postprocess.py   # XML object→signal transform
```

## Tech Stack

Python 3.11+ · Typer/Rich CLI · Pydantic settings · Loguru logging · Ruff linting

## Key Constraint

`netconvert` is an **external binary** (not pip-installable). Tests mock subprocess calls unless running integration tests.

```bash
uv run pytest -m "not integration"   # Unit tests (CI-safe)
uv run pytest -m integration         # Requires SUMO installed
```

## Deep Dive Docs

Read these when relevant to your task:

| File | When to Read |
|------|--------------|
| [agent_docs/architecture.md](agent_docs/architecture.md) | Understanding data flow, two-pass conversion |
| [agent_docs/netconvert.md](agent_docs/netconvert.md) | Adding parameters, SUMO installation |
| [agent_docs/testing.md](agent_docs/testing.md) | Debugging, test strategy |

## Critical Files

- `netconvert.py` — All ~40 netconvert CLI parameters
- `config.py` — Environment variable mappings
- `tests/data/ekas.osm` — Primary test input
