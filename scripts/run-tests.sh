#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

IMAGE="${INTELLICLAIM_IMAGE:-intelliclaim-extractor:phase1}"
NETWORK="${INTELLICLAIM_NETWORK:-intelliclaim-extractor_intelliclaim-net}"
DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://intelliclaim:intelliclaim@postgres:5432/intelliclaim}"

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    echo "==> Building Docker image $IMAGE..."
    docker build -t "$IMAGE" .
fi

COMMON_ARGS=(
    -v "$ROOT_DIR/src:/app/src:ro"
    -v "$ROOT_DIR/tests:/app/tests:ro"
    -v "$ROOT_DIR/pyproject.toml:/app/pyproject.toml:ro"
    -e SECRET_KEY=test-secret-key-for-pytest-runs-32chars
    -e OTEL_ENABLED=false
    -e PROMETHEUS_ENABLED=false
    -e PYTHONPATH=/app/src
    "$IMAGE"
)

echo "==> Running unit tests..."
docker run --rm "${COMMON_ARGS[@]}" \
    sh -c "pip install -q pytest pytest-asyncio pytest-cov httpx && \
           python -m pytest /app/tests -q --cov=src/intelliclaim --cov-fail-under=80 -m 'not integration'"

if docker network inspect "$NETWORK" >/dev/null 2>&1; then
    echo "==> Running repository integration tests..."
    docker run --rm --network "$NETWORK" "${COMMON_ARGS[@]}" \
        -e DATABASE_URL="$DATABASE_URL" \
        sh -c "pip install -q pytest pytest-asyncio pytest-cov httpx && \
               python -m pytest /app/tests/integration/repositories -ra -o addopts="
else
    echo "==> Skipping repository integration tests (start Postgres: docker compose up -d postgres)"
fi

echo "==> All tests passed."
