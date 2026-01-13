# Quick Command Reference

## Development Commands

### Setup and Installation

```bash
# Install dependencies
uv sync --all-extras

# Install in editable mode
uv pip install -e .
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=fhl_bible_api --cov-report=html

# Run specific test file
uv run pytest tests/test_client.py -v

# Run specific test
uv run pytest tests/test_client.py::test_get_verse_success -v
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Check code
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Type checking
uv run mypy src/fhl_bible_api
```

### Running Examples

```bash
# Run example script
uv run python example.py

# Run with specific Python version
uv run --python 3.12 python example.py
```

### Building

```bash
# Build package
uv build

# Clean build artifacts
rm -rf dist/ build/ *.egg-info
```

### Publishing

```bash
# Set environment variable for TestPyPI
# Windows (PowerShell)
$env:UV_PUBLISH_TOKEN = "your-testpypi-token"

# Linux/Mac
export UV_PUBLISH_TOKEN="your-testpypi-token"

# Publish to TestPyPI
uv publish --index testpypi

# Set environment variable for PyPI
# Windows (PowerShell)
$env:UV_PUBLISH_TOKEN = "your-pypi-token"

# Linux/Mac
export UV_PUBLISH_TOKEN="your-pypi-token"

# Publish to PyPI
uv publish

# Or use automated script (interactive)
uv run python publish.py
```

### Version Management

```bash
# Update version in pyproject.toml and __init__.py
# Then create git tag
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0
```

## Usage Examples

### Basic Usage

```python
from fhl_bible_api import FHLBibleClient

with FHLBibleClient() as client:
    response = client.get_verse(book_id=1, chapter=1, verse=1)
    print(response.records[0].text)
```

### Command Line Testing

```bash
# Quick test with Python
uv run python -c "from fhl_bible_api import FHLBibleClient; c = FHLBibleClient(); r = c.get_verse(1,1,1); print(r.records[0].text); c.close()"
```

## Git Commands

```bash
# Initial commit
git init
git add .
git commit -m "Initial commit: FHL Bible API v0.1.0"

# Create GitHub repo and push
git remote add origin https://github.com/YOUR_USERNAME/fhl-bible-api.git
git branch -M main
git push -u origin main

# Create release
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

## Troubleshooting

### Clear Cache

```bash
# Clear pytest cache
rm -rf .pytest_cache

# Clear ruff cache
rm -rf .ruff_cache

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### Reinstall

```bash
# Remove virtual environment
rm -rf .venv

# Recreate
uv sync --all-extras
```

## Environment Variables

```bash
# Windows (PowerShell)
# Set PyPI token
$env:UV_PUBLISH_TOKEN = "pypi-your_token_here"

# Set TestPyPI token
$env:UV_PUBLISH_TOKEN = "pypi-your_testpypi_token_here"

# Linux/Mac
# Set PyPI token
export UV_PUBLISH_TOKEN="pypi-your_token_here"

# Set TestPyPI token
export UV_PUBLISH_TOKEN="pypi-your_testpypi_token_here"

# Check if token is set (Windows PowerShell)
echo $env:UV_PUBLISH_TOKEN

# Check if token is set (Linux/Mac)
echo $UV_PUBLISH_TOKEN
```

## Quicinstallation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ fhl-bible-api

# Test local installation
uv pip install .

# Test from built wheel
uv pip install dist/fhl_bible_api-0.1.0-py3-none-any.whl

# Uninstall
uv pip uninstall fhl-bible-api
```

## Token Management

```bash
# Get tokens from:
# PyPI: https://pypi.org/manage/account/token/
# TestPyPI: https://test.pypi.org/manage/account/token/

# Security tips:
# 1. Never commit tokens to git
# 2. Use different tokens for PyPI and TestPyPI  
# 3. Set tokens as environment variables
# 4. Add *.token to .gitignore

# Create .env file (don't commit this!)
echo "UV_PUBLISH_TOKEN=your-token" > .env.local
echo "✅ All checks passed!"
```

## Installation Testing

```bash
# Test local installation
uv pip install .

# Test from built wheel
uv pip install dist/fhl_bible_api-0.1.0-py3-none-any.whl

# Uninstall
uv pip uninstall fhl-bible-api
```
