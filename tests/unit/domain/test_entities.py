"""Unit tests for domain entities."""

import pytest

from intelliclaim.domain.entities.document import Document
from intelliclaim.domain.entities.processing_job import ProcessingJob
from intelliclaim.domain.enums.document_status import DocumentStatus
from intelliclaim.domain.enums.document_type import DocumentType
from intelliclaim.domain.enums.job_status import JobStatus
from intelliclaim.domain.value_objects.document_id import DocumentId


@pytest.mark.unit
class TestDocument:
    @pytest.fixture
    def document(self) -> Document:
        return Document(
            id=DocumentId.generate(),
            filename="claim.pdf",
            content_type="application/pdf",
            document_type=DocumentType.PDF,
            file_size_bytes=1024,
            storage_path="/storage/claim.pdf",
        )

    def test_initial_status_is_pending(self, document: Document) -> None:
        assert document.status == DocumentStatus.PENDING

    def test_mark_status_updates_state(self, document: Document) -> None:
        document.mark_status(DocumentStatus.OCR_IN_PROGRESS)
        assert document.status == DocumentStatus.OCR_IN_PROGRESS

    def test_is_terminal_for_completed(self, document: Document) -> None:
        document.mark_status(DocumentStatus.COMPLETED)
        assert document.is_terminal() is True

    def test_is_terminal_for_failed(self, document: Document) -> None:
        document.mark_status(DocumentStatus.FAILED, error="OCR failed")
        assert document.is_terminal() is True
        assert document.error_message == "OCR failed"

    def test_is_not_terminal_when_processing(self, document: Document) -> None:
        document.mark_status(DocumentStatus.OCR_IN_PROGRESS)
        assert document.is_terminal() is False


@pytest.mark.unit
class TestProcessingJob:
    def test_create_job_is_queued(self) -> None:
        job = ProcessingJob.create(DocumentId.generate())
        assert job.status == JobStatus.QUEUED

    def test_mark_running_sets_task_id(self) -> None:
        job = ProcessingJob.create(DocumentId.generate())
        job.mark_running("celery-task-123")
        assert job.status == JobStatus.RUNNING
        assert job.celery_task_id == "celery-task-123"
        assert job.started_at is not None

    def test_mark_succeeded(self) -> None:
        job = ProcessingJob.create(DocumentId.generate())
        job.mark_running("task-1")
        job.mark_succeeded()
        assert job.status == JobStatus.SUCCEEDED
        assert job.completed_at is not None

    def test_mark_failed(self) -> None:
        job = ProcessingJob.create(DocumentId.generate())
        job.mark_failed("timeout")
        assert job.status == JobStatus.FAILED
        assert job.error_message == "timeout"
