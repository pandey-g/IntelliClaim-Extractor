# Database Schema

PostgreSQL 16 with async SQLAlchemy 2.0 and Alembic migrations.

## Entity Relationship

```mermaid
erDiagram
    documents ||--o{ document_pages : contains
    documents ||--o{ ocr_results : has
    documents ||--o{ extracted_fields : has
    documents ||--o{ processing_jobs : has
    documents ||--o{ audit_logs : tracks
    document_pages ||--o{ ocr_results : sources

    documents {
        uuid id PK
        string filename
        string content_type
        string document_type
        int file_size_bytes
        string storage_path
        string status
        int page_count
        text error_message
        timestamptz created_at
        timestamptz updated_at
    }

    document_pages {
        uuid id PK
        uuid document_id FK
        int page_number
        string storage_path
        int width
        int height
        timestamptz created_at
    }

    ocr_results {
        uuid id PK
        uuid document_id FK
        uuid page_id FK
        int page_number
        text full_text
        jsonb words
        float average_confidence
        timestamptz created_at
    }

    extracted_fields {
        uuid id PK
        uuid document_id FK
        string field_name
        text field_value
        float confidence
        int bbox_x
        int bbox_y
        int bbox_width
        int bbox_height
        int page_number
        timestamptz created_at
    }

    processing_jobs {
        uuid id PK
        uuid document_id FK
        string status
        string celery_task_id
        int retry_count
        text error_message
        timestamptz started_at
        timestamptz completed_at
        timestamptz created_at
    }

    audit_logs {
        uuid id PK
        uuid document_id FK
        string action
        string actor
        jsonb details
        timestamptz created_at
    }
```

## Tables

| Table | Purpose |
|-------|---------|
| `documents` | Uploaded file metadata and processing status |
| `document_pages` | Per-page preprocessed images |
| `ocr_results` | Tesseract output with word-level bounding boxes (JSONB) |
| `extracted_fields` | Structured insurance claim fields |
| `processing_jobs` | Celery async job tracking |
| `audit_logs` | Compliance and operational audit trail |

## Indexes

- `documents`: `status`, `created_at`
- `document_pages`: `document_id`, unique `(document_id, page_number)`
- `ocr_results`: `document_id`, `(document_id, page_number)`
- `extracted_fields`: `document_id`, `(document_id, field_name)`
- `processing_jobs`: `document_id`, `status`, `celery_task_id`
- `audit_logs`: `document_id`, `created_at`, `action`

## Migrations

```bash
# Apply all migrations
alembic upgrade head

# Create new migration (after model changes)
alembic revision --autogenerate -m "description"

# Rollback one revision
alembic downgrade -1
```

Initial migration: `alembic/versions/20250609_0001_initial_schema.py`

## Repository Layer

Domain entities are mapped to ORM models via `infrastructure/database/mappers.py`. Repository adapters in `infrastructure/repositories/` implement application port interfaces and are wired at startup through `infrastructure/bootstrap.py`.
