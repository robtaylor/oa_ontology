#!/bin/bash
# Install and run the OpenAccess Ontology Explorer

# Ensure we exit on any error
set -e

echo "OpenAccess Ontology Explorer - Installation and Execution"
echo "========================================================"

# Check for PDM
if command -v pdm &> /dev/null; then
    echo "✓ PDM found"
else
    echo "✗ PDM not found. Please install PDM first:"
    echo "  pip install pdm"
    echo "  or visit https://pdm-project.org/en/latest/usage/installation.html"
    exit 1
fi

# Install dependencies
echo -e "\nInstalling dependencies..."
pdm install

# Run the application
echo -e "\nRunning OpenAccess Ontology Explorer..."
pdm run oa-run-all

echo -e "\nDone!"