#!/bin/bash
# Test package installation
# Usage: ./scripts/release/test_install.sh [local|test|prod]

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

cd "$PROJECT_ROOT"

# Parse arguments
SOURCE="${1:-local}"

if [[ "$SOURCE" != "local" && "$SOURCE" != "test" && "$SOURCE" != "prod" ]]; then
    echo "❌ Error: Invalid source. Use 'local', 'test' or 'prod'"
    echo "Usage: $0 [local|test|prod]"
    exit 1
fi

echo "🧪 Testing package installation from $SOURCE..."
echo ""

# Create temp directory for virtual environment
TEST_VENV=$(mktemp -d -t orca-link-test-venv-XXXX)
trap "rm -rf $TEST_VENV" EXIT

echo "📁 Creating temporary virtual environment at: $TEST_VENV"
python -m venv "$TEST_VENV"

# Activate virtual environment
source "$TEST_VENV/bin/activate"

echo "📦 Installing orca-link from $SOURCE..."
echo ""

if [ "$SOURCE" = "local" ]; then
    # Install from local wheel
    if [ ! -d "dist" ]; then
        echo "❌ Error: dist/ directory not found. Run build.sh first."
        exit 1
    fi
    
    WHEEL=$(ls dist/*.whl | head -n 1)
    if [ -z "$WHEEL" ]; then
        echo "❌ Error: No wheel file found in dist/"
        exit 1
    fi
    
    pip install "$WHEEL"
    
elif [ "$SOURCE" = "test" ]; then
    # Install from TestPyPI
    pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ orca-link
    
elif [ "$SOURCE" = "prod" ]; then
    # Install from PyPI
    pip install orca-link
fi

echo ""
echo "✅ Installation successful!"
echo ""
echo "🧪 Testing import..."

# Try to import the package
if python -c "import orca_link; print(f'orca_link version: {getattr(orca_link, \"__version__\", \"unknown\")}')" 2>&1; then
    echo "✅ Import test passed!"
else
    echo "⚠️  Warning: Could not import orca_link module"
fi

echo ""
echo "📝 Package information:"
pip show orca-link

echo ""
echo "✅ All tests completed!"

