# Installation

Magneto provides multiple installation methods. You can choose the one that best suits your needs.

## Using uv (Recommended)

`uv` is a fast Python package manager that is fully compatible with `pyproject.toml`.

### 1. Install uv

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Sync Dependencies

Run in the project root directory:

```bash
# Sync dependencies and install project (development mode)
uv sync

# Run directly (no installation needed, uv manages environment automatically)
uv run magneto file.torrent
uv run magneto folder/ -r -v

# Install to current environment
uv pip install -e .

# Install development dependencies (if configured)
uv sync --extra dev

# View project information
uv tree
```

## Using pip

### Install from Source

```bash
# Clone repository (if not already done)
git clone https://github.com/mastaBriX/magneto.git
cd magneto

# Install project (pip automatically reads pyproject.toml)
pip install -e .
```

### Install Dependencies Directly

```bash
pip install bencode.py colorama
```

Then you can run `main.py` directly:

```bash
python main.py file.torrent
```

## Verify Installation

After installation, verify with the following commands:

```bash
# View version
magneto --version

# View help
magneto --help
```

If you see version information and help documentation, the installation was successful!

## Dependencies

### Required Dependencies

- **bencode.py >= 4.0.0**: Used for parsing torrent file format
- **colorama >= 0.4.0**: Used for Windows color output support (optional but recommended)

### Python Version Requirements

- Python 3.7 or higher
- Supports Python 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13

## Development Environment Setup

If you want to contribute to development or run tests:

```bash
# Using uv
uv sync --extra dev

# Or using pip
pip install -e ".[dev]"
```

Development dependencies include:
- `pytest >= 7.0.0` - Testing framework
- `pytest-cov >= 4.0.0` - Test coverage
- `black >= 23.0.0` - Code formatting
- `ruff >= 0.1.0` - Code linting

## Running Tests

```bash
# Run all tests
pytest

# Run tests and generate coverage report
pytest --cov=magneto --cov-report=html

# Run specific test file
pytest tests/test_core.py

# Verbose mode
pytest -v
```

## Troubleshooting

### Issue: Command 'magneto' not found

**Solution:**
- Ensure proper installation: `pip install -e .`
- Check Python environment: Make sure you're using the correct Python version
- Check PATH environment variable: Ensure Python's Scripts directory is in PATH

### Issue: Import error (bencode module not found)

**Solution:**
```bash
pip install bencode.py
```

### Issue: Colors not displaying on Windows

**Solution:**
```bash
pip install colorama
```

### Issue: Permission errors

**Solution:**
- Linux/macOS: Use `sudo` or virtual environment
- Windows: Run as administrator or use virtual environment

## Next Steps

After installation, you can:

- [Getting Started](/getting-started) - Learn basic usage
- [Usage Guide](/usage) - Learn all features

