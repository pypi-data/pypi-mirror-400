# pyPASreporter

CyberArk PAM reporting and analytics toolkit - the main package that brings together the pyPASreporter ecosystem.

## Installation

```bash
pip install pyPASreporter
```

Or with uv:

```bash
uv add pyPASreporter
```

This will install the main package along with its dependencies:
- pyPASreporter-EVDparser
- pyPASreporter-PACLIparser

## Usage

```python
import pypasreporter

# Use the unified API
pypasreporter.load_evd("/path/to/evd/exports")
pypasreporter.load_pacli("/path/to/pacli/exports")
```

### CLI

```bash
pypasreporter --help
pypasreporter load-evd /path/to/exports
pypasreporter load-pacli /path/to/exports
```

## Features

- Unified API for CyberArk PAM data processing
- EVD (Export Vault Data) parsing
- PACLI configuration parsing
- Report generation
- Analytics and insights

## Ecosystem Packages

| Package | Description |
|---------|-------------|
| [pyPASreporter](https://pypi.org/project/pyPASreporter/) | Main package (this one) |
| [pyPASreporter-EVDparser](https://pypi.org/project/pyPASreporter-EVDparser/) | EVD CSV export parser |
| [pyPASreporter-PACLIparser](https://pypi.org/project/pyPASreporter-PACLIparser/) | PACLI INI/XML config parser |

## License

MIT
