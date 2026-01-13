#!/bin/bash
# Quick test script for Unsiloed SDK

echo "🚀 Unsiloed SDK Quick Test"
echo ""

# Check if API key is set
if [ -z "$UNSILOED_API_KEY" ]; then
    echo "❌ UNSILOED_API_KEY is not set"
    echo ""
    echo "Please set your API key:"
    echo "  export UNSILOED_API_KEY='your-api-key-here'"
    echo ""
    echo "Get your API key from: https://www.unsiloed.ai/login"
    exit 1
fi

echo "✅ API key found: ${UNSILOED_API_KEY:0:10}..."
echo ""

# Find Python
PYTHON=""
if command -v python3 &> /dev/null; then
    PYTHON="python3"
elif command -v python &> /dev/null; then
    PYTHON="python"
else
    echo "❌ Python not found"
    exit 1
fi

echo "Using Python: $PYTHON"
echo ""

# Run test
cd "$(dirname "$0")"
$PYTHON test_sdk.py "$@"
