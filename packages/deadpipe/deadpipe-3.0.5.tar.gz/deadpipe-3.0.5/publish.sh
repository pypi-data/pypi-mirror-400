#!/bin/bash
# Publish script for Deadpipe Python SDK
# Usage: ./publish.sh [test|prod]

set -e

REPO="${1:-prod}"

if [ "$REPO" != "test" ] && [ "$REPO" != "prod" ]; then
    echo "Usage: $0 [test|prod]"
    echo "  test - Publish to TestPyPI"
    echo "  prod - Publish to PyPI (default)"
    exit 1
fi

echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info

echo "📦 Building package..."
python -m build

echo "📋 Built packages:"
ls -lh dist/

if [ "$REPO" == "test" ]; then
    echo "📤 Uploading to TestPyPI..."
    python -m twine upload --repository testpypi dist/*
    echo ""
    echo "✅ Done! Package published to TestPyPI"
    echo "📥 Test installation with:"
    echo "   pip install --index-url https://test.pypi.org/simple/ deadpipe"
else
    echo "📤 Uploading to PyPI..."
    python -m twine upload dist/*
    echo ""
    echo "✅ Done! Package published to PyPI"
    echo "📥 Install with: pip install deadpipe"
fi

