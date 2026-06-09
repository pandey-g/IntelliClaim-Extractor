# IntelliClaim Extractor

AI-powered document intelligence platform for insurance claim processing. Automatically extracts structured fields from scanned claim forms, policy documents, invoices, and supporting evidence.

## Features

- Document upload (PDF, PNG, JPG, TIFF)
- OpenCV preprocessing pipeline
- Tesseract OCR with bounding boxes
- LayoutLMv3 layout understanding
- Structured field extraction for insurance claims
- Asynchronous processing via Celery
- PostgreSQL persistence with Alembic migrations
- JWT + API key authentication
- OpenTelemetry tracing, Prometheus metrics, Grafana dashboards
- Production-grade error handling and structured JSON logging

## Architecture

Clean Architecture with four layers:

- **Domain** — entities, value objects, business rules (zero external dependencies)
- **Application** — use cases, DTOs, port interfaces, DI container
- **Infrastructure** — database, OCR, ML, storage, messaging adapters
- **API** — FastAPI routers, middleware, request/response schemas

See [docs/architecture.md](docs/architecture.md) for diagrams and design decisions.

## Prerequisites

- Python 3.12
- Poetry 1.8+
- Docker & Docker Compose
- Tesseract OCR (for local development)

## Local Setup

```bash
# Clone and install
git clone <repository-url>
cd IntelliClaim-Extractor
chmod +x scripts/setup-dev.sh
./scripts/setup-dev.sh

# Copy environment config
cp .env.example .env

# Run API server
poetry run uvicorn intelliclaim.main:app --reload
```

API docs: http://localhost:8000/docs

## Docker

```bash
# Start core services (API, PostgreSQL, Redis)
docker compose up -d

# With monitoring stack
docker compose --profile monitoring up -d

# With Celery workers (Phase 6+)
docker compose --profile workers up -d
```

| Service    | URL                    |
|------------|------------------------|
| API        | http://localhost:8000  |
| Prometheus | http://localhost:9090  |
| Grafana    | http://localhost:3000  |

## API Endpoints

| Method | Path                          | Description              |
|--------|-------------------------------|--------------------------|
| POST   | `/documents`                  | Upload document          |
| GET    | `/documents/{id}`             | Get document metadata    |
| GET    | `/documents/{id}/status`      | Processing status        |
| GET    | `/documents/{id}/extractions` | Extracted fields         |
| GET    | `/health`                     | Health check             |
| GET    | `/metrics`                    | Prometheus metrics       |

## Development

```bash
# Lint
poetry run ruff check src tests
poetry run ruff format src tests

# Type check
poetry run mypy src

# Tests
poetry run pytest

# Pre-commit
poetry run pre-commit run --all-files
```

## Project Structure

```
src/intelliclaim/
├── api/              # FastAPI HTTP layer
├── application/      # Use cases and port interfaces
├── domain/           # Business entities and rules
├── infrastructure/   # External system adapters
└── workers/          # Celery background tasks

tests/
├── unit/
└── integration/

docker/               # Docker overrides
monitoring/           # Prometheus & Grafana config
alembic/              # Database migrations
docs/                 # Architecture documentation
scripts/              # Development scripts
```

## Implementation Phases

| Phase | Scope                              | Status      |
|-------|------------------------------------|-------------|
| 1     | Project skeleton & architecture    | Complete    |
| 2     | Database & migrations              | Pending     |
| 3     | Document upload service            | Pending     |
| 4     | OCR pipeline                       | Pending     |
| 5     | LayoutLMv3 extraction              | Pending     |
| 6     | Celery background processing       | Pending     |
| 7     | Observability                      | Pending     |
| 8     | Testing                            | Pending     |
| 9     | Dockerization                      | Pending     |
| 10    | Production hardening               | Pending     |

## License

Proprietary — All rights reserved.
