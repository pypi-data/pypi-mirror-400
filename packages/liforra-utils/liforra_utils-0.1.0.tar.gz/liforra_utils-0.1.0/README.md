# lutils

Small logging and config helpers.

## Features
- Logging helper with consistent levels, optional color output, and optional file output.
- Config helper with dot-delimited keys and auto-create on missing values.
- Supports TOML/INI/JSON/YAML formats depending on installed parsers.
- Lightweight, minimal dependencies.

## Examples

Logging:
```python
import lutils

lutils.set_log_level("debug")
lutils.log("info", "Hello from lutils")
```

Config (auto-creates missing values when a default is given):
```python
import lutils

lutils.config.set("app.name", "beeper")
print(lutils.config.get("app.name"))
print(lutils.config.get("missing.value", "fallback"))
```

Config file selection (defaults to ./config.*):
```python
import lutils

lutils.config.set_name("settings")
lutils.config.set_path("./")
```

## Optional dependencies

`lutils` uses optional parsers if you have them installed:
- `toml` (only needed on Python < 3.11; Python 3.11+ uses `tomllib`)
- `PyYAML` for YAML support
- `coloredlogs` for colored log output

Install with extras (recommended):
```bash
pip install "lutils[toml,yaml,colors]"
```

Individual extras:
```bash
pip install "lutils[toml]"   # TOML on Python < 3.11
pip install "lutils[yaml]"   # YAML support
pip install "lutils[colors]" # coloredlogs output
```
