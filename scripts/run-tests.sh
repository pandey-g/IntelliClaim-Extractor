#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

IMAGE="${INTELLICLAIM_IMAGE:-intelliclaim-extractor:phase1}"

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    echo "==> Building Docker image $IMAGE..."
    docker build -t "$IMAGE" .
fi

echo "==> Running tests in Docker (Python 3.12)..."
docker run --rm \
    -v "$ROOT_DIR/tests:/app/tests:ro" \
    -v "$ROOT_DIR/pyproject.toml:/app/pyproject.toml:ro" \
    -e SECRET_KEY=test-secret-key-for-pytest-runs-32chars \
    -e OTEL_ENABLED=false \
    -e PROMETHEUS_ENABLED=false \
    -e PYTHONPATH=/app/src \
    "$IMAGE" \
    sh -c "pip install -q pytest pytest-asyncio pytest-cov httpx && python -m pytest /app/tests -ra --cov=src/intelliclaim --cov-report=term-missing --cov-fail-under=80"
