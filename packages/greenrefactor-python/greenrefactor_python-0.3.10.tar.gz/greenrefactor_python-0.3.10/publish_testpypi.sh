#!/bin/bash
set -e

# Change to the script's directory
cd "$(dirname "$0")"

echo "🚀 Preparing to publish greenrefactor-python to TestPyPI..."

# Clean previous builds
if [ -d "dist" ]; then
    echo "🧹 Cleaning dist/ directory..."
    rm -rf dist
fi

# Create and activate virtual environment
if [ ! -d ".venv_publish" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv .venv_publish
fi
source .venv_publish/bin/activate

# Install build tools
echo "📦 Installing build tools..."
pip install --upgrade build twine

# Build the package
echo "🔨 Building package..."
python3 -m build

# Upload to TestPyPI
echo "rz Uploading to TestPyPI..."
echo "ℹ️  You will be prompted for your TestPyPI username (__token__) and password (API Token)."
python3 -m twine upload --repository testpypi dist/*

# Deactivate
deactivate

echo "✅ Done! To install from TestPyPI:"
echo "pip install --index-url https://test.pypi.org/simple/ --no-deps greenrefactor-python==$(grep version pyproject.toml | cut -d'"' -f2)"
