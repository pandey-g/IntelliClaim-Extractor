"""Unit tests for insurance field pattern matching."""

import pytest

from intelliclaim.domain.enums.extraction_field import ExtractionField
from intelliclaim.infrastructure.ml.field_patterns import (
    FIELD_VALUE_PATTERNS,
    match_field_from_label,
    normalize_label,
)


@pytest.mark.unit
class TestFieldPatterns:
    def test_normalize_label_strips_colon(self) -> None:
        assert normalize_label("Claim ID:") == "claim id"

    def test_match_field_from_label(self) -> None:
        assert match_field_from_label("Policy Number:") == ExtractionField.POLICY_NUMBER
        assert match_field_from_label("Date of Incident") == ExtractionField.INCIDENT_DATE
        assert match_field_from_label("Unknown Field") is None

    def test_claim_id_pattern(self) -> None:
        pattern = FIELD_VALUE_PATTERNS[ExtractionField.CLAIM_ID]
        match = pattern.search("Reference CLM-12345 for processing")
        assert match is not None
        assert match.group(0) == "CLM-12345"
