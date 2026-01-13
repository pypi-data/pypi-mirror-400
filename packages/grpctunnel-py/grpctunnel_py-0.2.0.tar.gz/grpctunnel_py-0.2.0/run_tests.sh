#!/bin/bash
# Script to run tests and verify status

set -e

echo "================================"
echo " grpctunnel-py Test Suite"
echo "================================"
echo ""

# Kill any leftover processes
echo "Cleaning up any leftover processes..."
pkill -9 -f "pytest.*grpctunnel" 2>/dev/null || true
sleep 1

# Run tests
echo "Running test suite..."
echo ""

uv run pytest

echo ""
echo "================================"
echo " Test Summary"
echo "================================"
echo "✓ All tests completed"
echo ""
echo "Note: 6 tests are skipped (documented limitations):"
echo "  - 3 deadline enforcement tests (not yet implemented)"
echo "  - 1 concurrent reverse RPC test (known race condition)"
echo "  - 2 stream ID reuse tests (known limitation)"
echo ""
echo "See TEST_RESULTS.md for details"
