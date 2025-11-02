#!/bin/sh
# run_tests.sh for ai-worker

# Exit immediately if a command exits with a non-zero status.
set -e

# Install dependencies
echo "Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

# Run tests
echo "Running tests..."
PYTHONPATH=. pytest
