#!/bin/bash
#
# Run Fast LiteLLM Rust Acceleration Tests
#
# This script runs the focused test suite that verifies:
# 1. Rust extensions build and load correctly
# 2. Acceleration is applied to LiteLLM
# 3. Rust code paths are actually executed
#

set -e  # Exit on error

cd "$(dirname "$0")/.."

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Fast LiteLLM Rust Acceleration Test Suite"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if Rust is built
echo "🔍 Checking Rust build status..."
if .venv/bin/python -c "import fast_litellm; assert fast_litellm.RUST_ACCELERATION_AVAILABLE" 2>/dev/null; then
    echo "✓ Rust acceleration is available"
else
    echo "⚠️  Rust acceleration not available. Building..."
    .venv/bin/maturin develop --release
    echo "✓ Rust build complete"
fi
echo ""

# Run health check
echo "🏥 Running health check..."
.venv/bin/python -c "
import fast_litellm
import json
status = fast_litellm.health_check()
print(json.dumps(status, indent=2))
"
echo ""

# Run tests
echo "🧪 Running Rust acceleration tests..."
echo ""

if [ "$1" == "-v" ] || [ "$1" == "--verbose" ]; then
    # Verbose mode with output
    .venv/bin/pytest tests/test_rust_*.py -v -s
elif [ "$1" == "--coverage" ]; then
    # With coverage report
    .venv/bin/pytest tests/test_rust_*.py -v --cov=fast_litellm --cov-report=term --cov-report=html
    echo ""
    echo "📊 Coverage report generated in htmlcov/index.html"
else
    # Standard mode
    .venv/bin/pytest tests/test_rust_*.py -v
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ All Rust acceleration tests passed!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Summary:"
echo "  - Rust module: LOADED"
echo "  - Acceleration: APPLIED"
echo "  - Code paths: VERIFIED"
echo "  - LiteLLM: COMPATIBLE"
echo ""
echo "Run with -v for verbose output"
echo "Run with --coverage for coverage report"
