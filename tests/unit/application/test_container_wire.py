"""Unit tests for container wiring."""

from unittest.mock import MagicMock

import pytest

from intelliclaim.application.container import Container
from intelliclaim.infrastructure.config.settings import Settings


@pytest.mark.unit
class TestContainerWire:
    @pytest.fixture
    def wired_container(self) -> Container:
        container = Container(
            settings=Settings(secret_key="test-secret-key-for-pytest-runs-32chars"),
        )
        repo_mocks = {name: MagicMock() for name in [
            "document_repository",
            "document_page_repository",
            "ocr_result_repository",
            "extracted_field_repository",
            "processing_job_repository",
            "audit_log_repository",
        ]}
        service_mocks = {name: MagicMock() for name in [
            "document_storage",
            "ocr_service",
            "layout_analyzer",
            "field_extractor",
            "task_queue",
        ]}
        container.wire_repositories(**repo_mocks)
        container.wire_services(**service_mocks)
        return container

    def test_wire_initializes_container(self, wired_container: Container) -> None:
        wired_container.require_initialized()
        assert wired_container.documents is not None
        assert wired_container.document_pages is not None
        assert wired_container.audit_logs is not None
        assert wired_container.document_storage_service is not None
        assert wired_container.task_queue_service is not None

    def test_wire_repositories_only(self) -> None:
        container = Container(
            settings=Settings(secret_key="test-secret-key-for-pytest-runs-32chars"),
        )
        mocks = {name: MagicMock() for name in [
            "document_repository",
            "document_page_repository",
            "ocr_result_repository",
            "extracted_field_repository",
            "processing_job_repository",
            "audit_log_repository",
        ]}
        container.wire_repositories(**mocks)
        container.require_repositories_initialized()
        assert container.documents is not None
