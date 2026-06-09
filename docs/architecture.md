# Architecture

## Overview

IntelliClaim Extractor follows **Clean Architecture** with strict dependency inversion. Inner layers (Domain, Application) never depend on outer layers (Infrastructure, API).

```mermaid
flowchart TB
    subgraph External["External Systems"]
        Client[API Clients]
        PG[(PostgreSQL)]
        Redis[(Redis)]
        FS[File Storage]
        OCR[Tesseract]
        ML[LayoutLMv3]
    end

    subgraph API["API Layer"]
        Routes[FastAPI Routers]
        MW[Middleware]
        Schemas[Pydantic Schemas]
    end

    subgraph Application["Application Layer"]
        Services[Use Case Services]
        DTOs[DTOs]
        Ports[Port Interfaces]
        DI[DI Container]
    end

    subgraph Domain["Domain Layer"]
        Entities[Entities]
        VO[Value Objects]
        Enums[Enums]
        Exceptions[Domain Exceptions]
    end

    subgraph Infrastructure["Infrastructure Layer"]
        Repos[Repositories]
        Storage[Document Storage]
        OCRSvc[OCR Service]
        Layout[Layout Analyzer]
        Celery[Celery Tasks]
        DB[SQLAlchemy]
        OTel[OpenTelemetry]
    end

    Client --> Routes
    Routes --> Services
    Services --> Ports
    Services --> Entities
    Ports -.-> Repos
    Ports -.-> Storage
    Ports -.-> OCRSvc
    Repos --> DB
    DB --> PG
    Celery --> Redis
    OCRSvc --> OCR
    Layout --> ML
    Storage --> FS
```

## Layer Responsibilities

| Layer | Responsibility | Dependencies |
|-------|---------------|--------------|
| **Domain** | Business entities, value objects, rules | None |
| **Application** | Use cases, orchestration, port definitions | Domain only |
| **Infrastructure** | DB, OCR, ML, storage, messaging adapters | Application ports, Domain |
| **API** | HTTP, auth, validation, serialization | Application, Infrastructure config |

## Dependency Injection

The `Container` class wires infrastructure adapters at application startup. Services receive port interfaces, not concrete implementations:

```
FastAPI lifespan → Container.wire(repositories, services) → Route handlers use Container
```

## Document Processing Pipeline (Planned)

```mermaid
sequenceDiagram
    participant C as Client
    participant API as FastAPI
    participant Q as Redis/Celery
    participant W as Worker
    participant S as Storage
    participant OCR as Tesseract
    participant LM as LayoutLMv3
    participant DB as PostgreSQL

    C->>API: POST /documents (PDF/image)
    API->>S: Store original file
    API->>DB: Create document record
    API->>Q: Enqueue processing job
    API-->>C: 202 { document_id }

    Q->>W: Dispatch task
    W->>S: Retrieve document
    W->>W: OpenCV preprocessing
    W->>OCR: Extract text + bboxes
    W->>LM: Layout analysis
    W->>W: Field extraction + validation
    W->>DB: Persist results
```

## Project Structure

```
src/intelliclaim/
├── api/                    # HTTP interface
│   ├── dependencies/       # FastAPI DI
│   ├── middleware/         # Request ID, logging, errors
│   ├── routers/            # Route handlers
│   └── schemas/            # API request/response models
├── application/            # Use cases
│   ├── container.py        # DI container
│   ├── dto/                # Data transfer objects
│   ├── interfaces/         # Port definitions (repos, services)
│   └── services/           # Application services
├── domain/                 # Pure business logic
│   ├── entities/
│   ├── enums/
│   ├── exceptions/
│   └── value_objects/
├── infrastructure/         # External adapters
│   ├── config/
│   ├── database/
│   ├── logging/
│   └── observability/
└── workers/                # Celery background tasks
```

## Key Design Decisions

1. **Async-first**: FastAPI + async SQLAlchemy for I/O-bound document operations.
2. **Port/Adapter pattern**: OCR, layout analysis, and storage are swappable behind interfaces.
3. **UUID identifiers**: All primary keys use UUIDs for distributed system compatibility.
4. **Structured logging**: JSON logs with `request_id` and `document_id` correlation.
5. **Fail-fast validation**: Domain exceptions map to standardized HTTP error envelopes.
