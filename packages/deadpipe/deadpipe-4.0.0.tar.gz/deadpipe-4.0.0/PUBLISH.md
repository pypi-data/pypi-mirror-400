# Publishing Deadpipe Python SDK to PyPI

This guide explains how to build and upload the Deadpipe Python SDK to PyPI.

## Prerequisites

1. **PyPI Account**: You need an account on [PyPI](https://pypi.org) and [TestPyPI](https://test.pypi.org) (for testing)
2. **API Tokens**: Generate API tokens from your PyPI account settings
3. **Build Tools**: Install required build tools

## Setup

### 1. Install Build Tools

```bash
pip install --upgrade build twine
```

### 2. Configure PyPI Credentials

Create a `~/.pypirc` file (or update existing one) with your credentials:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-<your-pypi-api-token>

[testpypi]
username = __token__
password = pypi-<your-testpypi-api-token>
```

**Note**: Replace `<your-pypi-api-token>` and `<your-testpypi-api-token>` with your actual API tokens from PyPI.

Alternatively, you can pass credentials via environment variables or command-line flags (see below).

## Build Process

### 1. Navigate to SDK Directory

```bash
cd sdks/python
```

### 2. Clean Previous Builds (Optional)

```bash
rm -rf dist/ build/ *.egg-info
```

### 3. Update Version (if needed)

Edit `pyproject.toml` and update the version:

```toml
[project]
version = "2.0.2"  # Increment as needed
```

Also update the version in `deadpipe/__init__.py`:

```python
__version__ = "2.0.2"
```

### 4. Build Distribution Packages

```bash
python -m build
```

This creates:
- `dist/deadpipe-<version>-py3-none-any.whl` (wheel)
- `dist/deadpipe-<version>.tar.gz` (source distribution)

### 5. Verify Build

Check the built packages:

```bash
ls -lh dist/
```

You can also inspect the wheel contents:

```bash
python -m zipfile -l dist/deadpipe-*.whl
```

## Testing on TestPyPI (Recommended)

Before publishing to production PyPI, test on TestPyPI:

### 1. Upload to TestPyPI

```bash
python -m twine upload --repository testpypi dist/*
```

If you haven't configured `~/.pypirc`, use:

```bash
python -m twine upload --repository testpypi \
  --username __token__ \
  --password pypi-<your-testpypi-api-token> \
  dist/*
```

### 2. Test Installation from TestPyPI

```bash
pip install --index-url https://test.pypi.org/simple/ deadpipe
```

Or in a virtual environment:

```bash
python -m venv test-env
source test-env/bin/activate  # On Windows: test-env\Scripts\activate
pip install --index-url https://test.pypi.org/simple/ deadpipe
python -c "from deadpipe import track; print('Success!')"
deactivate
rm -rf test-env
```

## Publishing to Production PyPI

### 1. Final Verification

- [ ] Version number is correct in `pyproject.toml` and `__init__.py`
- [ ] README.md is up to date
- [ ] All tests pass
- [ ] TestPyPI installation works correctly

### 2. Upload to PyPI

```bash
python -m twine upload dist/*
```

If you haven't configured `~/.pypirc`, use:

```bash
python -m twine upload \
  --username __token__ \
  --password pypi-<your-pypi-api-token> \
  dist/*
```

### 3. Verify Publication

Check your package on PyPI:
- https://pypi.org/project/deadpipe/

Test installation:

```bash
pip install --upgrade deadpipe
python -c "from deadpipe import track; print('Success!')"
```

## Automated Script

You can create a simple script to automate the process:

```bash
#!/bin/bash
# publish.sh

set -e

echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info

echo "📦 Building package..."
python -m build

echo "📤 Uploading to PyPI..."
python -m twine upload dist/*

echo "✅ Done! Package published to PyPI"
```

Make it executable:

```bash
chmod +x publish.sh
```

## Troubleshooting

### Common Issues

1. **"Package already exists"**: Version number must be incremented
2. **"Invalid credentials"**: Check your API token in `~/.pypirc`
3. **"File already exists"**: Delete old files in `dist/` or increment version
4. **"Missing required files"**: Ensure `README.md` and `LICENSE` are present

### Version Conflicts

If you need to delete a version (only if it was just uploaded and has no downloads):

1. Go to https://pypi.org/manage/project/deadpipe/releases/
2. Find the version
3. Click "Delete" (only available for very recent uploads)

**Note**: Once a version has downloads, it cannot be deleted.

## Best Practices

1. **Always test on TestPyPI first** before publishing to production
2. **Use semantic versioning** (MAJOR.MINOR.PATCH)
3. **Update CHANGELOG** if you maintain one
4. **Tag releases in git** after publishing:
   ```bash
   git tag v2.0.2
   git push origin v2.0.2
   ```
5. **Keep build artifacts out of git** (add to `.gitignore`):
   ```
   dist/
   build/
   *.egg-info/
   ```

## CI/CD Integration

For automated publishing, you can use GitHub Actions. Example workflow:

```yaml
name: Publish to PyPI

on:
  release:
    types: [created]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      - name: Install build tools
        run: pip install build twine
      - name: Build package
        run: python -m build
        working-directory: ./sdks/python
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: python -m twine upload dist/*
        working-directory: ./sdks/python
```

## Quick Reference

```bash
# Build
cd sdks/python
python -m build

# Test on TestPyPI
python -m twine upload --repository testpypi dist/*

# Publish to PyPI
python -m twine upload dist/*

# Install and test
pip install --upgrade deadpipe
python -c "from deadpipe import track; print('Success!')"
```

