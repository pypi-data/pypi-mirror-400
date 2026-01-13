# bendlog

Utilities for analyzing Databend logs.

## Installation

```bash
# From the bendlog directory
pip install .

# Editable install (for development, changes take effect immediately)
pip install -e .

# With dev dependencies (pytest)
pip install -e ".[dev]"
```

## Usage

```python
from bendlog import read_lines

# Plain text file
for line in read_lines("file.log"):
    print(line)

# Zstd compressed
for line in read_lines("file.log.zst"):
    print(line)

# Tar.gz archive (reads all files inside)
for line in read_lines("logs.tar.gz"):
    print(line)

# Stdin
for line in read_lines("-"):
    print(line)
```

## Run Tests

```bash
pytest tests/ -v
```

## Publish to PyPI

```bash
# Install publish dependencies
pip install -e ".[publish]"

# Get API token from https://pypi.org/manage/account/token/
# or https://test.pypi.org/manage/account/token/ for TestPyPI

# Publish to TestPyPI first (recommended)
TWINE_PASSWORD=pypi-xxx ./publish.sh test

# Publish to PyPI
TWINE_PASSWORD=pypi-xxx ./publish.sh
```
