# IntelliClaim Extractor — Interview Prep Guide

Use this doc to **tell the project story**, survive **architect / senior engineer** deep dives, and answer **counter-questions** with confidence.

---

## 1. The 60-Second Pitch

> "I built **IntelliClaim Extractor** — a document intelligence platform for insurance claim processing. Insurers receive scanned PDFs and images (claim forms, invoices, policy docs). The system ingests those files, runs an OCR + layout analysis pipeline, and returns **structured fields** like claim ID, policy number, amounts, and dates.
>
> I designed it with **Clean Architecture** in Python — domain logic isolated from FastAPI, PostgreSQL, Tesseract, and LayoutLMv3. Everything external sits behind **port interfaces**, so OCR engines or ML models can be swapped without touching business rules.
>
> The pipeline is: upload → validate → render pages → OpenCV preprocessing → Tesseract OCR → LayoutLMv3 layout analysis → field extraction → validation → persist. I implemented it in **phased delivery** with tests, migrations, Docker, and observability hooks from day one."

**If they only remember one sentence:**  
*"Clean Architecture document pipeline that turns messy insurance scans into structured, auditable claim data."*

---

## 2. The 3-Minute Story (Use This Structure)

### Situation
Insurance claim intake is still heavily manual. Adjusters open PDFs, re-type claim numbers, policy IDs, and amounts into core systems. That is slow, error-prone, and hard to audit.

### Task
Build a **production-minded** backend — not a notebook demo — that:
- Accepts PDFs/images securely
- Extracts text and layout structure
- Maps results to **canonical insurance fields**
- Persists everything for audit and downstream integration

### Action (What *you* did — be specific)
1. **Architecture first** — Defined four layers (Domain, Application, Infrastructure, API) and port interfaces before writing adapters.
2. **Data model** — Designed PostgreSQL schema: documents, pages, OCR results (JSONB word boxes), extracted fields, processing jobs, audit logs. Alembic migrations from day one.
3. **Upload path** — File validation (extension, magic bytes, size, path traversal), local storage adapter, JWT + API key auth, audit logging.
4. **Processing pipeline** — Orchestrated in `DocumentProcessingService`: render → OCR → layout → extract → validate → mark `completed` or `failed`.
5. **ML pragmatism** — LayoutLMv3 for layout confidence + spatial key-value pairing; regex/synonym fallbacks when the model is unavailable or untrained on a form type.
6. **Quality** — Unit + integration tests, >80% coverage target, CI, structured JSON logging with request IDs.

### Result
- REST API with upload, process, status, OCR, and extraction endpoints
- Explicit document lifecycle (`pending` → … → `completed` / `failed`)
- Swappable adapters (Tesseract today; cloud OCR tomorrow)
- Foundation ready for async Celery workers and full observability (phased, not bolted on)

---

## 3. How to Open the Conversation

### With a **Senior Engineer** (implementation focus)
Lead with **one concrete flow**:

> "Let me walk through what happens when a client uploads a claim PDF and calls `POST /documents/{id}/process`."

Then trace: router → service → repositories → storage → OCR → layout → DB. Mention error handling and status transitions.

### With an **Architect** (design focus)
Lead with **boundaries and evolution**:

> "The core bet is **dependency inversion** — the application layer defines *what* it needs (IOCRService, ILayoutAnalyzer), infrastructure provides *how*. That lets us change Tesseract to AWS Textract or swap local disk for S3 without rewriting use cases."

Then mention phased delivery, async roadmap, and audit/compliance needs.

---

## 4. Architecture Talking Points (Memorize These)

| Topic | What to say |
|-------|-------------|
| **Why Clean Architecture?** | Insurance logic (field types, document states, validation rules) outlives any framework. FastAPI and SQLAlchemy are details; domain is not. |
| **Ports & adapters** | `ILayoutAnalyzer`, `IOCRService`, `IDocumentStorage`, repositories — all interfaces in Application; implementations in Infrastructure. |
| **DI Container** | Wired incrementally at startup: repos → storage → OCR → extraction. Fail-fast if something is not wired (`require_extraction_initialized()`). |
| **Domain purity** | Entities, value objects (`ConfidenceScore`, `BoundingBox`, `DocumentId`), enums — zero imports from FastAPI/SQLAlchemy. |
| **ORM isolation** | SQLAlchemy models + mappers in Infrastructure; repositories return domain entities. |
| **Sync vs async** | API and DB are async (FastAPI + asyncpg). CPU-heavy OCR/ML runs in thread pool (`asyncio.to_thread`) to avoid blocking the event loop. Celery planned for full background processing. |
| **Status machine** | `DocumentStatus` enum drives lifecycle; terminal states (`completed`, `failed`) block re-processing. |
| **Auditability** | `audit_logs` table + structured logs — who uploaded, when processing finished, field counts. |

---

## 5. Scenario Questions (Practice Out Loud)

### Scenario A: "Upload a 20-page claim PDF at 2 AM"

**Your answer:**
1. Client `POST /documents` with API key → validator checks size, extension, magic bytes.
2. File stored via `IDocumentStorage`; metadata in `documents` with status `pending`.
3. Today: client calls `POST /documents/{id}/process` (sync). Tomorrow (Phase 6): upload returns immediately; Celery worker runs the same `DocumentProcessingService` logic.
4. Each page rendered at 300 DPI, preprocessed, OCR'd; results in `ocr_results` with word-level JSONB bboxes.
5. Layout analyzer pairs keys/values spatially; field extractor maps to `ExtractionField` enum.
6. Validator checks date/amount formats; fields saved; status → `completed`.
7. If anything throws, status → `failed` with `error_message`; audit log still written.

---

### Scenario B: "Tesseract OCR quality is poor on handwritten forms"

**Your answer:**
- Short term: tune OpenCV pipeline (deskew, CLAHE, binarization); raise confidence thresholds; flag low-confidence fields for human review (validation layer lowers confidence, doesn't silently accept).
- Medium term: swap `IOCRService` implementation — Azure Document Intelligence, Google Document AI — without changing `DocumentProcessingService`.
- Long term: fine-tune LayoutLMv3 on insurer-specific forms; use human-in-the-loop feedback to retrain.

**Key phrase:** *"OCR is an adapter, not the core domain."*

---

### Scenario C: "Traffic spikes — 10,000 documents/hour"

**Your answer (honest + forward-looking):**
- **Today:** Sync processing is a deliberate Phase 1–5 choice for simplicity and testability; not production-scale for high volume.
- **Scale plan:**
  - Celery workers horizontally scaled behind Redis
  - Upload API returns 202 + job ID immediately
  - Object storage (S3) instead of local disk
  - Separate OCR/ML worker pool (GPU nodes for LayoutLMv3)
  - Rate limiting + queue depth monitoring
  - Idempotent job processing via `processing_jobs` + document status checks

---

### Scenario D: "Auditor asks: who changed what, and can we trust the extraction?"

**Your answer:**
- Every upload and processing completion writes to `audit_logs` (actor, action, document_id, details).
- Extracted fields store **confidence scores** and **bounding boxes** — traceable back to OCR tokens.
- Request ID middleware correlates HTTP logs with document_id in structured JSON logs.
- Failed validations reduce confidence rather than dropping fields silently.

---

## 6. Counter-Questions & Strong Answers

### Architecture & Design

**Q: Why Clean Architecture for a relatively small project? Isn't it over-engineering?**

> "For a demo, maybe. For insurance document processing, requirements change constantly — new form types, new OCR vendors, compliance rules, async processing. Clean Architecture pays off when **the expensive part is the domain**, not the HTTP layer. I paid a small upfront cost in interfaces and mappers so that swapping Tesseract or adding Celery doesn't become a rewrite. The container wiring is incremental — I didn't build everything on day one."

---

**Q: Why not just put everything in FastAPI route handlers?**

> "Route handlers should translate HTTP ↔ application DTOs. Business orchestration in handlers becomes untestable and couples you to FastAPI. My `DocumentProcessingService` has no FastAPI imports — I unit test it with mocked ports in milliseconds, without spinning up HTTP or Postgres."

---

**Q: How do you enforce dependency direction?**

> "Import rules: Domain imports nothing external. Application imports Domain only. Infrastructure implements Application ports. API calls Application services. MyPy + code review + the fact that domain entities don't know what SQLAlchemy is. If I need a DB query, it goes in a repository implementing `IDocumentRepository`."

---

**Q: Why a manual DI container instead of FastAPI-only Depends() or a framework like dependency-injector?**

> "FastAPI `Depends` is great at the HTTP boundary but doesn't help Celery workers or CLI scripts that run the same use cases. A single `Container` wired at lifespan startup lets workers and tests share the same composition root. I kept it as a dataclass — no magic — so senior engineers can read it in one file."

---

### System Design & Scale

**Q: Why PostgreSQL and not MongoDB for document JSON?**

> "I need **relational integrity**: document → pages → OCR results → extracted fields. JSONB handles OCR word arrays flexibly, but FK constraints and transactions matter for audit and partial failure recovery. Claim processing is workflow state + structured output, not a document store."

---

**Q: Why store files on disk instead of S3?**

> "Phase 3 used local storage behind `IDocumentStorage` — fastest path to a working adapter. Production would implement the same interface for S3 with pre-signed URLs. The application service calls `store()` and `retrieve()`; it doesn't care where bytes live."

---

**Q: Sync processing endpoint — wouldn't that timeout on large PDFs?**

> "Yes, for production multi-page PDFs under load. That's why `processing_jobs` and Celery are in the design. The sync endpoint was intentional for development and integration testing. The **same service layer** moves to workers — I'm not duplicating pipeline logic in tasks."

---

**Q: How would you handle partial failure on page 7 of 20?**

> "Today the whole document marks `failed`. Production improvement: per-page status, retry failed pages only, persist successful pages' OCR results, expose partial results via API. The schema already separates `document_pages` and per-page OCR — the data model supports it; orchestration would need enhancement."

---

### ML / OCR

**Q: Why LayoutLMv3 if you're also using regex and spatial heuristics?**

> "LayoutLMv3 base isn't fine-tuned on our insurance forms out of the box. Heuristics (colon-split lines, left/right columns) handle structured forms reliably. LayoutLMv3 adds embedding-based confidence and a path to fine-tuning. I didn't pretend the base model alone would solve extraction — I layered **deterministic fallbacks** under a swappable ML adapter."

---

**Q: How do you measure extraction accuracy?**

> "Honest answer: this project sets up the **evaluation harness** — stored ground-truth can be compared to extracted fields with confidence scores. Production would need labeled datasets per form type, precision/recall per `ExtractionField`, and human review queues for low-confidence fields. I'd track field-level metrics in Prometheus, not just API latency."

---

**Q: Why Tesseract and not a cloud OCR API?**

> "Cost, latency control, and offline capability for development. Tesseract behind `IOCRService` was the right default for a portfolio/production skeleton. Enterprise deployments often swap to Textract or Document AI — that's one adapter change."

---

**Q: GPU vs CPU for LayoutLMv3?**

> "Settings expose `layoutlm_device` (cpu/cuda/mps). Default CPU for Docker portability. Production ML workers would run on GPU nodes; API stays stateless on CPU. Model loads lazily so API pods that never process documents don't load torch weights."

---

### Security & Compliance

**Q: How do you secure the API?**

> "JWT for user sessions, API keys for service-to-service. Keys validated in dependency injection; settings bound per app instance for testability. Upload validation prevents path traversal and magic-byte spoofing. Production would add TLS, secrets manager, key rotation, and network policies."

---

**Q: Insurance data is sensitive — what about PII?**

> "Architecture supports it: encryption at rest on storage, DB column encryption for field values, retention policies, audit logs without storing raw file content in logs. I log document_id and metadata, not extracted patient names in debug output. Full HIPAA/GDPR compliance would add formal DPA, data residency, and access controls — the **audit trail and separation of concerns** are the foundation."

---

### Testing & Quality

**Q: How do you test without real ML models in CI?**

> "Unit tests mock `ILayoutAnalyzer` and `IFieldExtractor`. Spatial layout and field pattern modules are pure Python — fully tested without torch. ML adapters are coverage-omitted but isolated. Integration tests run OCR when Tesseract is present; skip gracefully otherwise."

---

**Q: 80% coverage — what's not covered?**

> "Repositories and ML inference paths in integration tests; some middleware and telemetry wiring. I prioritized domain, application services, and validation logic — where business bugs hurt most."

---

### Tradeoffs & "Why Not X?"

| They ask | You answer |
|----------|------------|
| **Django?** | Async-native FastAPI fits I/O-bound upload + status polling; automatic OpenAPI for integrators. |
| **Microservices?** | Monolith with clean module boundaries first — ops cost of 5 services isn't justified until scale demands it. Ports already define service boundaries if we split later. |
| **Event sourcing?** | Audit logs + status enum give traceability without event store complexity. Could add domain events later for Celery. |
| **GraphQL?** | REST + OpenAPI matches B2B insurance integrations; simple caching and gateway rules. |
| **Serverless Lambda?** | Cold start + large ML deps (torch, LayoutLM) are a poor fit; containerized workers are better. |

---

## 7. Honest Gaps (Say These Confidently)

Interviewers respect honesty framed as **roadmap**, not apology.

| Gap | How to say it |
|-----|----------------|
| Celery not wired yet | "Phase 6 — `ITaskQueue` port and `processing_jobs` table exist; worker implementation is next. Pipeline logic stays in application services." |
| Sync `/process` | "Dev/test convenience; production uses async enqueue." |
| LayoutLM not fine-tuned | "Base model + heuristics; production needs insurer-specific training data." |
| Local file storage | "S3 adapter behind same port for prod." |
| No human review UI | "API returns confidence; downstream workflow would route low-confidence fields to adjusters." |

**Never say:** "I didn't have time."  
**Say instead:** "I phased delivery — core architecture and pipeline first, async scale second."

---

## 8. Questions *You* Should Ask Them

Shows seniority:

1. "How do you handle **human-in-the-loop** when ML confidence is low on claims?"
2. "Are document pipelines **sync or queue-based** today, and where do bottlenecks show up?"
3. "How do you version **extracted field schemas** when core systems change?"
4. "What's your approach to **PII retention** and audit for regulated data?"
5. "Would this team split OCR/ML into a separate service, or keep it in the claim intake monolith?"

---

## 9. Red Flags to Avoid

| Don't | Do instead |
|-------|------------|
| Claim 99% extraction accuracy | Explain confidence scores, validation, and evaluation plan |
| Pretend Celery is fully done | Say port + schema ready, workers Phase 6 |
| Dump every technology name | Tie each tool to a **problem it solved** |
| Badmouth Tesseract/heuristics | Frame as pragmatic layering under swappable ports |
| Skip the business context | Always tie tech to **adjuster time saved** and **audit trail** |

---

## 10. Quick Reference — Pipeline & API

### Processing states
```
pending → preprocessing → ocr_in_progress → layout_analysis
  → extraction → validation → completed
(any step) → failed
```

### Key endpoints
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/documents` | Upload |
| POST | `/documents/{id}/process` | Run full pipeline (sync today) |
| GET | `/documents/{id}/status` | Poll state |
| GET | `/documents/{id}/ocr` | Raw OCR + word boxes |
| GET | `/documents/{id}/extractions` | Structured claim fields |

### Canonical extracted fields
`claim_id`, `policy_number`, `insured_name`, `claimant_name`, `address`, `claim_amount`, `invoice_amount`, `hospital_name`, `vehicle_number`, `incident_date`, `submission_date`

---

## 11. Closing Line (Memorable)

> "I treated this as **claim intake infrastructure**, not an OCR script. The architecture assumes vendors change, forms change, and volume grows — the domain rules and audit trail stay stable while adapters evolve."

---

*Good luck. Run through Scenarios A–D out loud once before the interview.*
