#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "==> Installing Poetry dependencies..."
poetry install

echo "==> Installing pre-commit hooks..."
poetry run pre-commit install

if [ ! -f .env ]; then
    echo "==> Creating .env from .env.example..."
    cp .env.example .env
fi

echo "==> Development environment ready."
echo "    Run: poetry run uvicorn intelliclaim.main:app --reload"
