#!/usr/bin/env bash
# Development helper script for task-ng
# Ensures the editable installation is up-to-date and runs task-ng
# Uses isolated development database to avoid touching production data

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# Set up development environment paths
DEV_CONFIG_DIR="$PROJECT_ROOT/.dev"
DEV_CONFIG_FILE="$DEV_CONFIG_DIR/config.toml"
DEV_DATA_DIR="$DEV_CONFIG_DIR/data"

# Create development directories if they don't exist
mkdir -p "$DEV_CONFIG_DIR"
mkdir -p "$DEV_DATA_DIR"

# Create minimal dev config if it doesn't exist
if [ ! -f "$DEV_CONFIG_FILE" ]; then
    cat > "$DEV_CONFIG_FILE" << 'EOF'
# Development configuration for task-ng
# This file is automatically created by scripts/dev.sh

[data]
location = ".dev/data"

[ui]
color = true

[default]
command = "list"
EOF
    echo "📝 Created development config at $DEV_CONFIG_FILE"
fi

# Clear Python cache to ensure fresh imports
find src -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find src -name "*.pyc" -delete 2>/dev/null || true

# Reinstall in editable mode (suppress output unless there's an error)
if ! poetry run pip install -e . > /dev/null 2>&1; then
    echo "Error: Failed to install task-ng in editable mode" >&2
    exit 1
fi

# Run task-ng with development config and data directory
# Use environment variables to override default locations
TASKNG_CONFIG_FILE="$DEV_CONFIG_FILE" \
TASKNG_DATA_DIR="$DEV_DATA_DIR" \
poetry run task-ng "$@"
