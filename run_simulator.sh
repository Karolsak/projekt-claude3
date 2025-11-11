#!/bin/bash
# Launcher script for Enhanced Economic Dispatch Simulator

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║      Enhanced Economic Dispatch Simulator - Launcher          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Checking dependencies..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.7 or higher."
    exit 1
fi
echo "✓ Python3 found: $(python3 --version)"

# Check if numpy is installed
if ! python3 -c "import numpy" 2>/dev/null; then
    echo "❌ NumPy not found. Installing..."
    pip install numpy
fi
echo "✓ NumPy installed"

# Check if matplotlib is installed
if ! python3 -c "import matplotlib" 2>/dev/null; then
    echo "❌ Matplotlib not found. Installing..."
    pip install matplotlib
fi
echo "✓ Matplotlib installed"

echo ""
echo "Starting Enhanced Economic Dispatch Simulator..."
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Run the enhanced simulator
python3 economic_dispatch_simulator_enhanced.py

echo ""
echo "Simulator closed."
