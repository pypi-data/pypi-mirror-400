#!/usr/bin/env bash

set -e

ruff check .

# Unset custom index URLs to use public PyPI only
unset UV_INDEX_URL
unset UV_EXTRA_INDEX_URL
unset PIP_INDEX_URL
unset PIP_EXTRA_INDEX_URL

uv sync --extra dev

# Run Python tests
python -m unittest discover tests/ -v

# Install JavaScript dependencies
echo ""
echo "Installing JavaScript dependencies..."
npm ci

# Run JavaScript tests
echo ""
echo "Running JavaScript tests..."
npm test

# Run JavaScript tests with coverage
echo ""
echo "Running JavaScript tests with coverage..."
npm run test:coverage