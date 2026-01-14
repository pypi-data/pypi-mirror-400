# Architecture

## Module Overview

```text
src/osm_to_xodr/
├── __init__.py      # Package version
├── cli.py           # Typer CLI entry point
├── config.py        # Pydantic settings (env vars + .env)
├── converter.py     # Orchestrates the 3-step conversion
├── netconvert.py    # Subprocess wrapper for SUMO netconvert
└── postprocess.py   # XML post-processing for signals
```

## Design Decisions

1. **External Dependency**: `netconvert` is a system binary from SUMO, wrapped via `subprocess.run()`.

2. **Two-Pass Conversion**: netconvert runs twice:
   - Pass 1: Extract traffic signs → temp XML
   - Pass 2: Generate OpenDRIVE with signs as polygon input

3. **Signal Post-processing**: netconvert creates `<object>` elements; CARLA expects `<signal>`. `postprocess.py` does this XML transformation.

4. **Configuration Hierarchy**: CLI args > env vars > `.env` file > defaults

## Data Flow

```text
Input: tests/data/ekas.osm
         │
         ▼
┌─────────────────────────────┐
│ netconvert (pass 1)         │
│ --street-sign-output        │
└─────────────────────────────┘
         │
         ▼
Temp: tmp/ekas_signs.xml
         │
         ▼
┌─────────────────────────────┐
│ netconvert (pass 2)         │
│ --opendrive-output          │
│ --polygon-files (signs)     │
└─────────────────────────────┘
         │
         ▼
Intermediate: output/ekas.xodr (with <object> elements)
         │
         ▼
┌─────────────────────────────┐
│ postprocess.py              │
│ Convert objects to signals  │
└─────────────────────────────┘
         │
         ▼
Output: output/ekas.xodr (with <signal> elements)
```

## Key Files

| File | Purpose |
|------|---------|
| `netconvert.py` | All netconvert parameters (~40) |
| `config.py` | Pydantic settings with env var names |
| `tests/data/ekas.osm` | Primary test input file |
| `justfile` | Task runner commands |
