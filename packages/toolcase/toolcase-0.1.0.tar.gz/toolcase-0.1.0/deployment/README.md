# Deployment

Scripts and configuration for publishing toolcase to PyPI.

## Quick Publish

```bash
# Set token as env var (recommended)
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-token-here

# Build and publish
./deployment/publish.sh
```

## Token Configuration

### Option 1: Environment Variables (Recommended)
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-xxx
```

### Option 2: `.pypirc` File
Create `~/.pypirc`:
```ini
[pypi]
username = __token__
password = pypi-xxx
```

### Option 3: Keyring
```bash
pip install keyring
keyring set https://upload.pypi.org/legacy/ __token__
```

## Commands

### Build Only
```bash
python3 -m build
```

### Publish to TestPyPI First
```bash
./deployment/publish.sh --test
pip install -i https://test.pypi.org/simple/ toolcase
```

### Publish to Production PyPI
```bash
./deployment/publish.sh
```

### Skip Build (upload existing dist/)
```bash
./deployment/publish.sh --skip-build
```

## Version Bumping

Update version in both:
- `pyproject.toml` → `version = "X.Y.Z"`
- `src/toolcase/__init__.py` → `__version__ = "X.Y.Z"`

## Pre-publish Checklist

- [ ] Version updated in both files
- [ ] Tests passing: `pytest`
- [ ] Type check: `mypy src/`
- [ ] Lint: `ruff check src/`
- [ ] CHANGELOG updated (if applicable)
- [ ] Git tag created: `git tag v0.1.0`
