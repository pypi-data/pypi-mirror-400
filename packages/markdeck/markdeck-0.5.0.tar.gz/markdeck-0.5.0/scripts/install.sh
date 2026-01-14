#!/usr/bin/env bash

set -e

# Example: Only run in remote environments
if [ "$CLAUDE_CODE_REMOTE" != "true" ]; then
    echo "Skipping installation script in local environment."
    exit 0
fi

uv sync --extra dev