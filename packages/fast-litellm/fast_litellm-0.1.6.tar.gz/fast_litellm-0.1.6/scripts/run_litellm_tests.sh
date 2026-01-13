#!/bin/bash
# Run LiteLLM tests with Fast LiteLLM acceleration enabled
# This validates that Fast LiteLLM doesn't break any LiteLLM functionality

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LITELLM_DIR="${PROJECT_ROOT}/.litellm"

echo "============================================="
echo "Fast LiteLLM - Integration Test Runner"
echo "============================================="
echo ""

# Check if we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    # Check if .venv exists
    if [ -d "$PROJECT_ROOT/.venv" ]; then
        echo "⚠️  Virtual environment detected but not activated"
        echo ""
        echo "Activating virtual environment..."
        source "$PROJECT_ROOT/.venv/bin/activate"
        echo "✅ Virtual environment activated"
        echo ""
    else
        echo "⚠️  No virtual environment detected"
        echo ""
        echo "Please run setup first:"
        echo "  ./scripts/setup_litellm.sh"
        echo ""
        echo "Or activate your virtual environment:"
        echo "  source .venv/bin/activate"
        exit 1
    fi
fi

# Check if LiteLLM is set up
if [ ! -d "$LITELLM_DIR" ]; then
    echo "❌ LiteLLM not found at: $LITELLM_DIR"
    echo ""
    echo "Please run setup first:"
    echo "  ./scripts/setup_litellm.sh"
    exit 1
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "📦 Installing pytest..."
    pip install pytest pytest-asyncio || {
        echo "❌ Failed to install pytest"
        exit 1
    }
fi

# Check if Fast LiteLLM is built
echo "🔍 Checking Fast LiteLLM build..."
if ! python -c "import fast_litellm._rust" 2>/dev/null; then
    echo "⚠️  Fast LiteLLM Rust extensions not found. Building..."

    # Check if maturin is installed
    if ! command -v maturin &> /dev/null; then
        echo "📦 Installing maturin..."
        pip install maturin || {
            echo "❌ Failed to install maturin"
            exit 1
        }
    fi

    cd "$PROJECT_ROOT"
    maturin develop || {
        echo "❌ Failed to build Fast LiteLLM"
        echo ""
        echo "This could be due to:"
        echo "  • Missing Rust toolchain (install from https://rustup.rs)"
        echo "  • Missing system dependencies"
        echo ""
        echo "To install Rust:"
        echo "  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
        exit 1
    }
fi

echo "✅ Fast LiteLLM is built and ready"
echo ""

# Get test path from arguments or use default
TEST_PATH="${1:-tests/}"
PYTEST_ARGS="${@:2}"  # Additional pytest arguments

echo "📋 Test Configuration:"
echo "  LiteLLM Path: $LITELLM_DIR"
echo "  Test Path: $TEST_PATH"
echo "  Fast LiteLLM: $(python -c "import fast_litellm; print(fast_litellm.__version__)")"
echo "  LiteLLM: $(cd "$LITELLM_DIR" && python -c "import litellm; print(litellm.__version__)" 2>/dev/null || echo "unknown")"
if [[ -n "$VIRTUAL_ENV" ]]; then
    echo "  Virtual Env: $VIRTUAL_ENV"
fi
echo ""

# Ensure fast_litellm is in PYTHONPATH
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Change to LiteLLM directory
cd "$LITELLM_DIR"

# Create a conftest.py to enable fast_litellm
cat > conftest.py << 'EOF'
"""
Pytest configuration to enable Fast LiteLLM acceleration
"""
import sys
import pytest

# Import fast_litellm before any tests run
import fast_litellm

def pytest_configure(config):
    """Configure pytest to use Fast LiteLLM"""
    print("\n" + "="*60)
    print("Fast LiteLLM Integration Test Session")
    print("="*60)
    print(f"Fast LiteLLM Version: {fast_litellm.__version__}")
    print(f"Rust Acceleration: {fast_litellm.RUST_ACCELERATION_AVAILABLE}")

    if fast_litellm.RUST_ACCELERATION_AVAILABLE:
        try:
            status = fast_litellm.get_patch_status()
            print(f"Patches Applied: {status.get('applied', False)}")
        except:
            pass
    print("="*60 + "\n")

def pytest_sessionfinish(session, exitstatus):
    """Print performance stats after tests complete"""
    try:
        import fast_litellm
        if fast_litellm.RUST_ACCELERATION_AVAILABLE:
            print("\n" + "="*60)
            print("Fast LiteLLM Performance Summary")
            print("="*60)
            try:
                stats = fast_litellm.get_performance_stats()
                print(f"Performance data collected: {len(stats)} components")

                recommendations = fast_litellm.get_recommendations()
                if recommendations:
                    print("\nOptimization Recommendations:")
                    for rec in recommendations[:5]:  # Show top 5
                        print(f"  • {rec.get('message', rec)}")
            except Exception as e:
                print(f"Could not retrieve performance stats: {e}")
            print("="*60 + "\n")
    except:
        pass
EOF

echo "🧪 Running LiteLLM tests with Fast LiteLLM acceleration..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Verify imports work from this directory
echo "🔍 Verifying imports..."
python -c "import sys; sys.path.insert(0, '$PROJECT_ROOT'); import fast_litellm; print(f'✅ fast_litellm {fast_litellm.__version__} accessible')" || {
    echo "❌ Cannot import fast_litellm"
    echo ""
    echo "PYTHONPATH: $PYTHONPATH"
    echo "Python path:"
    python -c "import sys; print('\n'.join(sys.path))"
    exit 1
}

echo ""

# Run pytest with the test path
pytest "$TEST_PATH" \
    -v \
    --tb=short \
    --disable-warnings \
    --import-mode=importlib \
    $PYTEST_ARGS || {

    EXIT_CODE=$?
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "❌ Tests failed with exit code: $EXIT_CODE"
    echo ""
    echo "This could indicate:"
    echo "  • Fast LiteLLM broke some functionality (needs investigation)"
    echo "  • LiteLLM tests have failing tests (check without acceleration)"
    echo "  • Test environment issues (API keys, network, etc.)"
    echo ""
    echo "To debug:"
    echo "  1. Run LiteLLM tests without acceleration to establish baseline"
    echo "  2. Compare results with acceleration enabled"
    echo "  3. Check logs for acceleration-specific errors"

    # Cleanup
    rm -f conftest.py
    exit $EXIT_CODE
}

# Cleanup
rm -f conftest.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Tests completed successfully!"
echo ""
echo "Fast LiteLLM acceleration did not break LiteLLM functionality."
