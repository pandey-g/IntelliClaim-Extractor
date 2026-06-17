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
        ocr_mocks = {name: MagicMock() for name in [
            "page_renderer",
            "image_preprocessor",
            "ocr_service",
        ]}
        service_mocks = {name: MagicMock() for name in [
            "layout_analyzer",
            "field_extractor",
            "task_queue",
        ]}
        storage_mock = MagicMock()
        container.wire_repositories(**repo_mocks)
        container.wire_storage(document_storage=storage_mock)
        container.wire_ocr(**ocr_mocks)
        container.wire_extraction(
            layout_analyzer=service_mocks["layout_analyzer"],
            field_extractor=service_mocks["field_extractor"],
        )
        container.wire_services(**service_mocks)
        return container

    def test_wire_initializes_container(self, wired_container: Container) -> None:
        wired_container.require_initialized()
        assert wired_container.documents is not None
        assert wired_container.document_pages is not None
        assert wired_container.audit_logs is not None
        assert wired_container.document_storage_service is not None
        assert wired_container.ocr_service_instance is not None
        assert wired_container.page_renderer_service is not None
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

    def test_wire_extraction_only(self) -> None:
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
        container.wire_repositories(**repo_mocks)
        container.wire_storage(document_storage=MagicMock())
        container.wire_ocr(
            page_renderer=MagicMock(),
            image_preprocessor=MagicMock(),
            ocr_service=MagicMock(),
        )
        container.wire_extraction(
            layout_analyzer=MagicMock(),
            field_extractor=MagicMock(),
        )
        container.require_extraction_initialized()
        assert container.layout_analyzer_service is not None
        assert container.field_extractor_service is not None

    def test_wire_ocr_requires_storage(self) -> None:
        container = Container(
            settings=Settings(secret_key="test-secret-key-for-pytest-runs-32chars"),
        )
        container.wire_ocr(
            page_renderer=MagicMock(),
            image_preprocessor=MagicMock(),
            ocr_service=MagicMock(),
        )
        with pytest.raises(RuntimeError, match="Storage not initialized"):
            container.require_ocr_initialized()
