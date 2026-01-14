#!/usr/bin/env bash
set -e

echo "=== Lint ==="
poetry run ruff check src/ tests/

echo ""
echo "=== Format ==="
poetry run ruff format --check src/ tests/

echo ""
echo "=== Type Check ==="
poetry run mypy src/

echo ""
echo "=== Tests ==="
poetry run pytest -v --cov --cov-report=term-missing --cov-report=xml

echo ""
echo "✓ All CI checks passed"
