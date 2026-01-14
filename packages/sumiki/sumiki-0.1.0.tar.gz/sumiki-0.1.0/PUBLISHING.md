# Publishing Sumiki (Lyzr SDK) to PyPI

**PyPI Package Name**: sumiki
**Import Name**: from lyzr import Studio
**Install**: pip install sumiki

## Quick Guide

### 1. Install Build Tools
```bash
uv pip install build twine
```

### 2. Clean Previous Builds
```bash
rm -rf dist/ build/ *.egg-info
```

### 3. Build the Package
```bash
uv build
# Or: python3 -m build
```

This creates:
- `dist/sumiki-0.1.0.tar.gz`
- `dist/sumiki-0.1.0-py3-none-any.whl`

### 4. Check the Package
```bash
twine check dist/*
```

### 5. Upload to PyPI

**Option A: Using API Token**
```bash
# Set token as environment variable
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YOUR-API-TOKEN-HERE

# Upload
twine upload dist/*
```

**Option B: Interactive**
```bash
twine upload dist/*
# Username: __token__
# Password: pypi-YOUR-TOKEN
```

### 6. Verify Installation
```bash
pip install sumiki
python3 -c "from lyzr import Studio; print('Success!')"
```

---

## Testing on TestPyPI First (Recommended)

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test install
pip install --index-url https://test.pypi.org/simple/ sumiki

# Test it works
python3 -c "from lyzr import Studio; print('Works!')"
```

---

## Complete Workflow

```bash
# 1. Update version
# Edit pyproject.toml and lyzr/__init__.py

# 2. Clean and build
rm -rf dist/ build/ *.egg-info
uv build

# 3. Check
twine check dist/*

# 4. Test on TestPyPI (optional)
twine upload --repository testpypi dist/*

# 5. Upload to PyPI
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YOUR-TOKEN
twine upload dist/*

# 6. Test installation
pip install sumiki
```

---

## PyPI Credentials

### Get API Token
1. Go to https://pypi.org/manage/account/
2. Scroll to "API tokens"
3. Click "Add API token"
4. Name: "lyzr-sdk"
5. Scope: "Entire account"
6. Copy the token (starts with `pypi-`)

### Configure ~/.pypirc (Optional)
```bash
cat > ~/.pypirc << 'EOF'
[pypi]
username = __token__
password = pypi-YOUR-TOKEN-HERE
EOF

chmod 600 ~/.pypirc
```

---

## Version Updates

Before each release, update version in:
1. `pyproject.toml` - `version = "0.1.1"`
2. `lyzr/__init__.py` - `__version__ = "0.1.1"`

---

## Package Name

- **PyPI Name**: `lyzr`
- **Import Name**: `from lyzr import Studio`
- **Install**: `pip install sumiki`

Done! 🎉
