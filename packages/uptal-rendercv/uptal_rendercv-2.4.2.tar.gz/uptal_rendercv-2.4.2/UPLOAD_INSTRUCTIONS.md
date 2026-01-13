# Upload Instructions for uptal-rendercv

## Overview
This package has been configured to upload to PyPI as `uptal-rendercv` with the `[full]` optional dependencies.

## Changes Made
1. ✅ **Package Name**: Changed from `rendercv` to `uptal-rendercv`
2. ✅ **Phone Validation**: Disabled phone number validation
3. ✅ **CLI Command**: Updated to `uptal-rendercv`
4. ✅ **Optional Dependencies**: Already configured for `[full]` extra
5. ✅ **Build Configuration**: Tested and working

## Upload Steps

### 1. Setup PyPI Account
- Make sure you have a PyPI account
- Configure your API token: `pip install twine && twine configure`

### 2. Test Build (Already Done)
```bash
python -m build
```
This creates the wheel and source distribution in `dist/`

### 3. Upload to TestPyPI (Recommended First)
```bash
twine upload --repository testpypi dist/*
```
Test installation:
```bash
pip install --index-url https://test.pypi.org/simple/ "uptal-rendercv[full]"
```

### 4. Upload to Production PyPI
```bash
twine upload dist/*
```

### 5. Verify Installation
```bash
pip install "uptal-rendercv[full]"
uptal-rendercv --help
```

## Package Details
- **Name**: `uptal-rendercv`
- **Version**: `2.4.1`
- **Optional Dependencies**: `[full]` includes CLI, PDF generation, and fonts
- **CLI Command**: `uptal-rendercv`
- **Python Requirements**: `>=3.10`

## Files Created
- `uptal_rendercv-2.4.1-py3-none-any.whl` (124KB)
- `uptal_rendercv-2.4.1.tar.gz` (7.4MB)

## Post-Upload
1. Update any documentation to reference `uptal-rendercv` instead of `rendercv`
2. Test installation on a clean environment
3. Update any CI/CD pipelines that reference the old package name