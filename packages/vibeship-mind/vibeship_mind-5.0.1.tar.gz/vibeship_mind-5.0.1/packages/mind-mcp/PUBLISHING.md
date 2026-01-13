# Publishing mind-mcp to PyPI

## Prerequisites

1. **PyPI Account**: Create at https://pypi.org/account/register/
2. **TestPyPI Account**: Create at https://test.pypi.org/account/register/
3. **GitHub Environments**: Set up `pypi` and `testpypi` environments with trusted publisher

## Setup Trusted Publisher (Recommended)

PyPI now supports "Trusted Publishers" which uses OIDC - no API tokens needed.

### On PyPI:

1. Go to https://pypi.org/manage/account/publishing/
2. Add new pending publisher:
   - **Project name**: `mind-mcp`
   - **Owner**: `vibeship` (GitHub org/user)
   - **Repository**: `mind`
   - **Workflow name**: `publish-mind-mcp.yml`
   - **Environment**: `pypi`

### On TestPyPI:

1. Go to https://test.pypi.org/manage/account/publishing/
2. Same settings but environment: `testpypi`

### On GitHub:

1. Go to repo Settings > Environments
2. Create `pypi` environment
3. Create `testpypi` environment
4. Optionally add protection rules (require approval, etc.)

## Publishing Methods

### Method 1: Git Tag (Recommended for releases)

```bash
# Update version in pyproject.toml first
cd packages/mind-mcp
# Edit pyproject.toml: version = "0.1.1"

# Commit and tag
git add pyproject.toml
git commit -m "chore(mcp): bump version to 0.1.1"
git tag mcp-v0.1.1
git push origin master --tags
```

This triggers the workflow automatically.

### Method 2: Manual Dispatch (For testing)

1. Go to Actions > "Publish mind-mcp to PyPI"
2. Click "Run workflow"
3. Check "Publish to TestPyPI instead of PyPI" for testing
4. Click "Run workflow"

### Method 3: Local Build & Upload

```bash
cd packages/mind-mcp

# Build
python -m build

# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ mind-mcp

# If all good, upload to PyPI
twine upload dist/*
```

## Version Numbering

Follow semantic versioning:
- `0.1.0` - Initial release
- `0.1.1` - Bug fixes
- `0.2.0` - New features (backward compatible)
- `1.0.0` - Stable release / breaking changes

## Post-Publish Verification

```bash
# Wait a few minutes for PyPI to update

# Test installation
pip install mind-mcp
# or
uvx mind-mcp --version

# Test functionality
uvx mind-mcp --setup
```

## Troubleshooting

### "Package already exists"
Version numbers are immutable on PyPI. Bump the version and try again.

### "Invalid or non-existent authentication"
Check that the trusted publisher is configured correctly on PyPI.

### "Filename has been previously used"
Delete local `dist/` folder and rebuild with new version.

## Checklist for New Releases

- [ ] Update version in `pyproject.toml`
- [ ] Update CHANGELOG if exists
- [ ] Test locally: `pip install -e . && mind-mcp --version`
- [ ] Commit changes
- [ ] Create git tag: `git tag mcp-vX.Y.Z`
- [ ] Push with tags: `git push origin master --tags`
- [ ] Verify GitHub Actions passes
- [ ] Test: `uvx mind-mcp --version` shows new version
- [ ] Update documentation if needed
