#!/bin/bash
# Install and run the OpenAccess Ontology Explorer

# Ensure we exit on any error
set -e

echo "OpenAccess Ontology Explorer - Installation and Execution"
echo "========================================================"

# Check for PDM
if command -v pdm &> /dev/null; then
    echo "✓ PDM found"
    INSTALL_CMD="pdm install"
    RUN_CMD="pdm run oa-run-all"
elif command -v pip &> /dev/null; then
    echo "✓ pip found (PDM not found)"
    INSTALL_CMD="pip install -e ."
    RUN_CMD="oa-run-all"
else
    echo "✗ Neither PDM nor pip found. Please install PDM or pip first."
    exit 1
fi

# Install dependencies
echo -e "\nInstalling dependencies..."
$INSTALL_CMD

# Run the application
echo -e "\nRunning OpenAccess Ontology Explorer..."
$RUN_CMD

echo -e "\nDone!"