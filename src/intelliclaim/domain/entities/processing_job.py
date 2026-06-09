"""Processing job domain entity."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from intelliclaim.domain.enums.job_status import JobStatus
from intelliclaim.domain.value_objects.document_id import DocumentId


@dataclass
class ProcessingJob:
    """Represents an asynchronous document processing job."""

    id: UUID
    document_id: DocumentId
    status: JobStatus = JobStatus.QUEUED
    celery_task_id: str | None = None
    retry_count: int = 0
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(cls, document_id: DocumentId) -> "ProcessingJob":
        """Factory method for creating a new processing job."""
        return cls(id=uuid4(), document_id=document_id)

    def mark_running(self, celery_task_id: str) -> None:
        """Mark job as running with associated Celery task ID."""
        self.status = JobStatus.RUNNING
        self.celery_task_id = celery_task_id
        self.started_at = datetime.now(UTC)

    def mark_succeeded(self) -> None:
        """Mark job as successfully completed."""
        self.status = JobStatus.SUCCEEDED
        self.completed_at = datetime.now(UTC)

    def mark_failed(self, error: str) -> None:
        """Mark job as failed with error message."""
        self.status = JobStatus.FAILED
        self.error_message = error
        self.completed_at = datetime.now(UTC)
