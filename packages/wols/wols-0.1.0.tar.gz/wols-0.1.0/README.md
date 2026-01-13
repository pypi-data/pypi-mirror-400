# WOLS - WeMush Open Labeling Standard

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](https://opensource.org/licenses/Apache-2.0)

The official Python implementation of the WeMush Open Labeling Standard (WOLS) v1.1.0 for specimen tracking in mushroom cultivation.

## Features

- **Core Module**: Create, parse, validate, and serialize specimen labels
- **QR Codes**: Generate and scan QR codes (PNG, SVG, base64)
- **Encryption**: AES-256-GCM encryption for sensitive data
- **CLI**: Command-line interface for all operations
- **Type Safe**: Full type annotations with PEP 561 support

## Installation

### Basic Installation (Core Only)

```bash
# Using UV (recommended)
uv add wols

# Using pip
pip install wols
```

### With Optional Features

```bash
# QR code support
uv add "wols[qr]"

# CLI support
uv add "wols[cli]"

# Encryption support
uv add "wols[crypto]"

# Everything
uv add "wols[all]"
```

### Requirements

- Python 3.12 or later
- No required dependencies for core module

## Quick Examples

### Create a Specimen (Library)

```python
from wols import create_specimen, SpecimenType, GrowthStage, to_json

# Create a specimen
specimen = create_specimen(
    type=SpecimenType.SUBSTRATE,
    species="Pleurotus ostreatus",
    strain="Blue Oyster",
    stage=GrowthStage.COLONIZATION,
    batch="BATCH-2026-001",
)

# Print the ID
print(f"Created: {specimen.id}")
# Output: Created: wemush:clx1abc123def456

# Serialize to JSON-LD
json_str = to_json(specimen, indent=2)
print(json_str)
```

### Create a Specimen (CLI)

```bash
wols create \
  --species "Pleurotus ostreatus" \
  --type SUBSTRATE \
  --strain "Blue Oyster" \
  --stage COLONIZATION \
  --output specimen.json
```

### Generate QR Code (Library)

```python
from wols import create_specimen, SpecimenType
from wols.qr import generate_qr_png

specimen = create_specimen(
    type=SpecimenType.SUBSTRATE,
    species="Pleurotus ostreatus",
)

# Generate QR code
qr_bytes = generate_qr_png(specimen)

# Save to file
with open("label.png", "wb") as f:
    f.write(qr_bytes)
```

### Validate Specimen (Library)

```python
from wols import validate_specimen, parse_specimen

json_str = '{"@context": "...", "@type": "Specimen", ...}'
specimen = parse_specimen(json_str)

result = validate_specimen(specimen)
if result.valid:
    print("Valid specimen!")
else:
    for error in result.errors:
        print(f"{error.path}: {error.message}")
```

### Validate Specimen (CLI)

```bash
wols validate specimen.json
```

## Verification

After installation, verify the library works:

```bash
# Check version
python -c "import wols; print(wols.__version__)"

# Check CLI (if installed)
wols --version

# Run a quick test
python -c "
from wols import create_specimen, SpecimenType, to_json
s = create_specimen(type=SpecimenType.CULTURE, species='Test')
print('Success:', s.id)
"
```

## Documentation

- [Full API Documentation](./specs/001-wols-python-library/contracts/python-api.md)
- [CLI Reference](./specs/001-wols-python-library/contracts/cli-api.md)
- [Data Model](./specs/001-wols-python-library/data-model.md)
- [Quickstart Guide](./specs/001-wols-python-library/quickstart.md)

## Development

```bash
# Clone the repository
git clone https://github.com/wemush/specimen-labels-py.git
cd specimen-labels-py

# Install with development dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Run linting
uv run ruff check src tests
uv run ruff format --check src tests

# Run type checking
uv run mypy src
```

## License

Apache 2.0 License - see [LICENSE](LICENSE) for details.
