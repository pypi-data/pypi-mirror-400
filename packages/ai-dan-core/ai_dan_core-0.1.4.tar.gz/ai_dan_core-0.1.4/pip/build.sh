#!/bin/bash
# Build script for ai-dan pip package

set -e

echo "Building ai-dan wheel..."
cd "$(dirname "$0")/.."

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build the wheel
python3 -m pip install --upgrade build
python3 -m build

echo ""
echo "Build complete! Wheel files:"
ls -lh dist/

echo ""
echo "To install locally:"
echo "  pip install dist/ai_dan-*.whl"
echo ""
echo "To upload to PyPI:"
echo "  pip install twine"
echo "  twine upload dist/*"
