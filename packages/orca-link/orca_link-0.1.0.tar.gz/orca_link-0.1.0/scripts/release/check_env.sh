#!/bin/bash
# Check if the environment is ready for releasing to PyPI
# Usage: ./scripts/release/check_env.sh

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

cd "$PROJECT_ROOT"

echo "🔍 Checking OrcaLink release environment..."
echo ""

ERRORS=0
WARNINGS=0

# Check Python
echo "📌 Checking Python..."
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    echo "   ✅ Python $PYTHON_VERSION found"
else
    echo "   ❌ Python not found"
    ERRORS=$((ERRORS + 1))
fi

# Check build tool
echo ""
echo "📌 Checking build tool..."
if python -m build --version &> /dev/null; then
    BUILD_VERSION=$(python -m build --version 2>&1)
    echo "   ✅ $BUILD_VERSION"
else
    echo "   ⚠️  'build' not installed. Run: pip install build"
    WARNINGS=$((WARNINGS + 1))
fi

# Check twine
echo ""
echo "📌 Checking twine..."
if command -v twine &> /dev/null; then
    TWINE_VERSION=$(twine --version 2>&1 | head -n 1)
    echo "   ✅ $TWINE_VERSION"
else
    echo "   ⚠️  'twine' not installed. Run: pip install twine"
    WARNINGS=$((WARNINGS + 1))
fi

# Check pyproject.toml
echo ""
echo "📌 Checking pyproject.toml..."
if [ -f "pyproject.toml" ]; then
    echo "   ✅ pyproject.toml found"
    
    # Check for required fields
    if grep -q 'name = "orca-link"' pyproject.toml; then
        echo "   ✅ Project name correct: orca-link"
    else
        echo "   ⚠️  Project name might not be 'orca-link' in pyproject.toml"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    if grep -q 'version = "' pyproject.toml; then
        VERSION=$(grep -Po '(?<=version = ")[^"]*' pyproject.toml)
        echo "   ✅ Version: $VERSION"
    else
        echo "   ❌ Version not found in pyproject.toml"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "   ❌ pyproject.toml not found"
    ERRORS=$((ERRORS + 1))
fi

# Check .pypirc
echo ""
echo "📌 Checking PyPI credentials..."
if [ -f "$HOME/.pypirc" ]; then
    echo "   ✅ ~/.pypirc found"
    
    # Check permissions
    PERMS=$(stat -c %a "$HOME/.pypirc" 2>/dev/null || stat -f %OLp "$HOME/.pypirc")
    if [[ "$PERMS" == *"600"* ]] || [[ "$PERMS" == *"rw-------"* ]]; then
        echo "   ✅ Permissions correct (600)"
    else
        echo "   ⚠️  Permissions may be too open: $PERMS (should be 600)"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo "   ⚠️  ~/.pypirc not found"
    echo "      Copy from: cp $SCRIPT_DIR/.pypirc.example ~/.pypirc"
    echo "      Then edit with your API tokens"
    WARNINGS=$((WARNINGS + 1))
fi

# Check GitHub workflows
echo ""
echo "📌 Checking GitHub Actions workflow..."
if [ -f ".github/workflows/publish.yml" ]; then
    echo "   ✅ GitHub Actions workflow found"
else
    echo "   ⚠️  GitHub Actions workflow not found at .github/workflows/publish.yml"
    WARNINGS=$((WARNINGS + 1))
fi

# Check scripts
echo ""
echo "📌 Checking release scripts..."
SCRIPTS=("clean.sh" "build.sh" "check.sh" "upload_test.sh" "upload_prod.sh" "release.sh" "bump_version.sh" "test_install.sh")
MISSING=0
for script in "${SCRIPTS[@]}"; do
    if [ -f "$SCRIPT_DIR/$script" ]; then
        if [ -x "$SCRIPT_DIR/$script" ]; then
            echo "   ✅ $script"
        else
            echo "   ⚠️  $script not executable"
            WARNINGS=$((WARNINGS + 1))
        fi
    else
        echo "   ❌ $script missing"
        MISSING=$((MISSING + 1))
    fi
done

if [ $MISSING -gt 0 ]; then
    ERRORS=$((ERRORS + MISSING))
fi

# Summary
echo ""
echo "================================"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ Environment is ready!"
    echo "================================"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Configure ~/.pypirc with your API tokens"
    echo "   2. Run: ./scripts/release/release.sh test"
    echo "   3. Test installation: ./scripts/release/test_install.sh test"
    echo "   4. Release to PyPI: ./scripts/release/release.sh prod"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "⚠️  Environment has $WARNINGS warnings"
    echo "================================"
    echo ""
    echo "Run 'make test-release' to proceed anyway"
    exit 0
else
    echo "❌ Environment has $ERRORS errors and $WARNINGS warnings"
    echo "================================"
    echo ""
    echo "Please fix the errors above before proceeding"
    exit 1
fi

