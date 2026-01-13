# Publishing to PyPI Guide

This guide explains how to publish the `fhl-bible-api` package to PyPI.

## Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org/
2. **TestPyPI Account** (for testing): Create an account at https://test.pypi.org/
3. **API Tokens**: Generate API tokens from your account settings:
   - PyPI token for production releases
   - TestPyPI token for testing
4. **uv Installed**: Make sure `uv` is installed and up to date

## Steps to Publish

### 1. Configure Credentials

#### Option A: Using Environment Variables (Recommended)

For **production PyPI**:
```bash
# Windows (PowerShell)
$env:UV_PUBLISH_TOKEN = "your-pypi-token"

# Linux/Mac
export UV_PUBLISH_TOKEN="your-pypi-token"
```

For **TestPyPI**:
```bash
# Windows (PowerShell)
$env:UV_PUBLISH_TOKEN = "your-testpypi-token"

# Linux/Mac
export UV_PUBLISH_TOKEN="your-testpypi-token"
```

#### Option B: Using uv Config

```bash
# Set PyPI token in uv configuration
uv config set pypi.token <your-token>
```

**Note**: When using environment variables, `UV_PUBLISH_TOKEN` takes precedence over config file settings.

### 2. Run Pre-publish Checks

```bash
# Run all tests
uv run pytest --cov=fhl_bible_api

# Check code quality
uv run ruff check .

# Format code
uv run ruff format .

# Type checking (optional)
uv run mypy src/fhl_bible_api
```

### 3. Build the Package

```bash
# Build wheel and source distribution
uv build
```

This creates:
- `dist/fhl_bible_api-0.1.0-py3-none-any.whl` (wheel)
- `dist/fhl_bible_api-0.1.0.tar.gz` (source)

### 4. Test on TestPyPI (Recommended)

First, publish to TestPyPI to verify everything works:

```bash
# Set TestPyPI token as environment variable
# Windows (PowerShell)
$env:UV_PUBLISH_TOKEN = "your-testpypi-token"

# Linux/Mac
export UV_PUBLISH_TOKEN="your-testpypi-token"

# Publish to TestPyPI
uv publish --index testpypi
```

**Important Notes**roduction PyPI

Once everything is verified on TestPyPI:

```bash
# Set PyPI token as environment variable
# Windows (PowerShell)
$env:UV_PUBLISH_TOKEN = "your-pypi-token"

# Linux/Mac
export UV_PUBLISH_TOKEN="your-pypi-token"

# Publish to PyPI
uv publish
```

Or use the automated script:

```bash
# Run the publish script (interactive)
uv run python publish.py
```

**Security Note**: Never commit your tokens to version control!
### 5. Publish to PyPI

Once everything is verified:

```bash
# Publish to PyPI
uv publish
```

Or use the automated script:

```bash
# Run the publish script (interactive)
uv run python publish.py
```

### 6. Verify Publication

Check that your package is available:

```bash
# Search for your package
pip search fhl-bible-api

# Install from PyPI
pip install fhl-bible-api
```

Visit your package page: https://pypi.org/project/fhl-bible-api/

## Version Management

When releasing new versions:

1. Update version in `pyproject.toml`:
   ```toml
   version = "0.2.0"
   ```
**Check token validity**: Make sure your token is correct and not expired
2. **Verify environment variable**: Ensure `UV_PUBLISH_TOKEN` is set correctly
   ```bash
   # Windows (PowerShell)
   echo $env:UV_PUBLISH_TOKEN
   
   # Linux/Mac
   echo $UV_PUBLISH_TOKEN
   ```
3. **Check token permissions**: Token must have upload permissions
4. **TestPyPI vs PyPI**: Make sure you're using the correct token for the target index
   __version__ = "0.2.0"
   ```

3. Create a git tag:
   ```bash
   git tag -a v0.2.0 -m "Release version 0.2.0"
   git push origin v0.2.0
   ```

4. Build and publish:
   ```bash
   uv build
   uv publish
   ```

## Troubleshooting

### Authentication Errors

If you get authentication errors:

1. Make sure your token is correct
2. Use `__token__` as username when using tokens
3. Check token permissions (must have upload permissions)

### Build Errors

If build fails:

1. Ensure `pyproject.toml` is valid
2. Check all files are included in `src/` directory
3. Verify dependencies are correct

### Upload Errors

   - Use a different version number for testing (e.g., 0.1.0rc1)
   - Verify installation and basic functionality
   - Clean up test releases if needed

5. **Documentation**: Update README.md before releasing

6. **Environment Variables**: Use environment variables for tokens, never hardcode them

7. **Token Security**:
   - Keep tokens secret
   - Use different tokens for PyPI and TestPyPI
   - Rotate tokens periodically
   - Add `*.token` to `.gitignore`
- You cannot re-upload the same version
- Increment the version number and try again

## Best Practices

1. **Semantic Versioning**: Follow semver (MAJOR.MINOR.PATCH)
   - MAJOR: Breaking changes
   - MINOR: New features (backward compatible)
   - PATCH: Bug fixes

2. **Changelog**: Maintain a CHANGELOG.md file

3. **Git Tags**: Create git tags for each release

4. **Testing**: Always test on TestPyPI first

5. **Documentation**: Update README.md before releasing

## Automated Publishing

For CI/CD automation, see GitHub Actions example:

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
      - name: Build and publish
        env:
          UV_PUBLISH_TOKEN: ${{ secrets.PYPI_TOKEN }}
        run: |
          uv build
          uv publish
```

## Resources

- [PyPI Documentation](https://pypi.org/help/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Python Packaging Guide](https://packaging.python.org/)
