#!/usr/bin/env bash
# Refresh the editable installation after making code changes
# Run this whenever you edit Python files to ensure changes take effect

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "🧹 Clearing Python cache..."
find src -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find src -name "*.pyc" -delete 2>/dev/null || true

echo "📦 Reinstalling in editable mode..."
if poetry run pip install -e . > /dev/null 2>&1; then
    echo "✅ Editable installation refreshed successfully!"
else
    echo "❌ Error: Failed to install task-ng in editable mode" >&2
    exit 1
fi
