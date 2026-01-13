# Task: Publishing Preparation

## Status: NOT STARTED

## Objective

Prepare the package for PyPI publication: verify metadata, build distributions, test installation.

## Context

- All code, tests, and docs complete
- Package should be ready to publish but NOT published yet
- Need PyPI account and API token for actual publish

---

## Deliverables

1. Verify `pyproject.toml` metadata is complete
2. Build wheel and sdist
3. Test installation from built package
4. Document publish process

---

## Phase 1: Verify Metadata

Check `pyproject.toml` has all required fields:

```bash
cd packages/surfacedocs-python

# View current metadata
cat pyproject.toml
```

Required fields:
- [ ] `name` = "surfacedocs"
- [ ] `version` = "0.1.0"
- [ ] `description` - one-line description
- [ ] `readme` = "README.md"
- [ ] `license` = "MIT"
- [ ] `requires-python` >= "3.9"
- [ ] `authors` with name and email
- [ ] `keywords` - relevant search terms
- [ ] `classifiers` - PyPI classifiers
- [ ] `dependencies` - httpx
- [ ] `project.urls` - Homepage, Repository

---

## Phase 2: Build Package

```bash
cd packages/surfacedocs-python

# Install build tool
pip install build

# Build wheel and sdist
python -m build

# Check output
ls -la dist/
# Should see:
# - surfacedocs-0.1.0-py3-none-any.whl
# - surfacedocs-0.1.0.tar.gz
```

---

## Phase 3: Verify Build

```bash
# Check wheel contents
unzip -l dist/surfacedocs-0.1.0-py3-none-any.whl

# Check sdist contents
tar -tzf dist/surfacedocs-0.1.0.tar.gz
```

Should include:
- `surfacedocs/__init__.py`
- `surfacedocs/client.py`
- `surfacedocs/schema.py`
- `surfacedocs/prompt.py`
- `surfacedocs/exceptions.py`

---

## Phase 4: Test Installation

```bash
# Create fresh virtual environment
python -m venv /tmp/test-surfacedocs
source /tmp/test-surfacedocs/bin/activate

# Install from wheel
pip install dist/surfacedocs-0.1.0-py3-none-any.whl

# Test imports
python -c "
from surfacedocs import SurfaceDocs, DOCUMENT_SCHEMA, SYSTEM_PROMPT
from surfacedocs.exceptions import SurfaceDocsError
print('DOCUMENT_SCHEMA keys:', list(DOCUMENT_SCHEMA.keys()))
print('SYSTEM_PROMPT length:', len(SYSTEM_PROMPT))
print('SurfaceDocs:', SurfaceDocs)
print('All imports successful!')
"

# Check installed version
pip show surfacedocs

# Clean up
deactivate
rm -rf /tmp/test-surfacedocs
```

---

## Phase 5: Validate with Twine

```bash
pip install twine

# Check package for PyPI compatibility
twine check dist/*

# Should output:
# Checking dist/surfacedocs-0.1.0-py3-none-any.whl: PASSED
# Checking dist/surfacedocs-0.1.0.tar.gz: PASSED
```

---

## Phase 6: Document Publish Process

Create `PUBLISHING.md` in package root:

```markdown
# Publishing surfacedocs to PyPI

## Prerequisites

1. PyPI account at https://pypi.org
2. API token from Account Settings → API tokens
3. `twine` installed: `pip install twine`

## Build

```bash
cd packages/surfacedocs-python
pip install build
python -m build
```

## Test Upload (TestPyPI)

```bash
# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Test install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ surfacedocs
```

## Production Upload

```bash
# Upload to PyPI
twine upload dist/*

# Verify
pip install surfacedocs
```

## Version Bump

1. Update version in `pyproject.toml`
2. Update `__version__` in `__init__.py`
3. Commit and tag: `git tag v0.1.0`
4. Build and upload

## Authentication

Set up `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-...

[testpypi]
username = __token__
password = pypi-...
```

Or use environment variables:
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-...
```
```

---

## Verification Checklist

```bash
# Run all checks
cd packages/surfacedocs-python

# 1. Tests pass
pytest -v

# 2. Build succeeds
python -m build

# 3. Twine check passes
twine check dist/*

# 4. Fresh install works
python -m venv /tmp/test && source /tmp/test/bin/activate
pip install dist/*.whl
python -c "from surfacedocs import SurfaceDocs; print('OK')"
deactivate && rm -rf /tmp/test
```

---

## Definition of Done

- [ ] `pyproject.toml` has all required metadata
- [ ] `python -m build` produces wheel and sdist
- [ ] `twine check dist/*` passes
- [ ] Package installs from wheel in fresh venv
- [ ] All imports work after installation
- [ ] `PUBLISHING.md` documents the publish process
- [ ] Package is ready to publish (but NOT published)
