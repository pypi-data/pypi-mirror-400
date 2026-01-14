# Testing Strategy

## Test Categories

- **Unit tests** (`tests/test_*.py`): Test individual modules, mock subprocess calls
- **Integration tests** (`tests/test_integration.py`): Require real `netconvert`, marked with `@pytest.mark.integration`

## Running Tests

```bash
# Unit tests only (CI-safe, no SUMO required)
uv run pytest -m "not integration"

# Integration tests (requires SUMO installed)
uv run pytest -m integration

# All tests
uv run pytest
```

## Quick Validation

```bash
just lint && just test   # Linting + unit tests
just convert-test        # Full conversion with ekas.osm
ls -la output/ekas.xodr  # Verify output
```

## Debugging Conversion Issues

1. Run with verbose: `osm-to-xodr convert input.osm -v`
2. Keep intermediate files: `osm-to-xodr convert input.osm -v -k`
3. Check the temporary signs XML in `tmp/` directory
4. Examine netconvert stderr output in logs
