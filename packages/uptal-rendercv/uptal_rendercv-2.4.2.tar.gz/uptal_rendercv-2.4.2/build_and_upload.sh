#!/bin/bash

# Build and upload script for uptal-rendercv
set -e

echo "Building uptal-rendercv package..."

# Clean any previous builds
rm -rf dist/ build/ *.egg-info/

# Install build dependencies
pip install --upgrade build twine

# Build the package
python -m build

echo "Package built successfully!"
echo "Files in dist/:"
ls -la dist/

echo ""
echo "To upload to PyPI:"
echo "1. Test upload to TestPyPI first:"
echo "   twine upload --repository testpypi dist/*"
echo ""
echo "2. Then upload to production PyPI:"
echo "   twine upload dist/*"
echo ""
echo "Make sure you have your PyPI credentials configured!"