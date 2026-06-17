"""Insurance claim field label patterns for structured extraction."""

import re
from re import Pattern

from intelliclaim.domain.enums.extraction_field import ExtractionField

FIELD_SYNONYMS: dict[ExtractionField, tuple[str, ...]] = {
    ExtractionField.CLAIM_ID: (
        "claim id",
        "claim number",
        "claim no",
        "claim #",
        "claim ref",
    ),
    ExtractionField.POLICY_NUMBER: (
        "policy number",
        "policy no",
        "policy #",
        "policy id",
    ),
    ExtractionField.INSURED_NAME: (
        "insured name",
        "name of insured",
        "policyholder",
        "insured",
    ),
    ExtractionField.CLAIMANT_NAME: (
        "claimant name",
        "claimant",
        "patient name",
    ),
    ExtractionField.ADDRESS: (
        "address",
        "mailing address",
        "residential address",
    ),
    ExtractionField.CLAIM_AMOUNT: (
        "claim amount",
        "total claim",
        "amount claimed",
    ),
    ExtractionField.INVOICE_AMOUNT: (
        "invoice amount",
        "invoice total",
        "bill amount",
    ),
    ExtractionField.HOSPITAL_NAME: (
        "hospital name",
        "hospital",
        "medical facility",
    ),
    ExtractionField.VEHICLE_NUMBER: (
        "vehicle number",
        "registration number",
        "license plate",
        "vehicle reg",
    ),
    ExtractionField.INCIDENT_DATE: (
        "incident date",
        "date of incident",
        "accident date",
        "loss date",
    ),
    ExtractionField.SUBMISSION_DATE: (
        "submission date",
        "date submitted",
        "filing date",
    ),
}

FIELD_VALUE_PATTERNS: dict[ExtractionField, Pattern[str]] = {
    ExtractionField.CLAIM_ID: re.compile(
        r"\b(?:CLM|CLAIM)[-\s]?[A-Z0-9]{4,12}\b",
        re.IGNORECASE,
    ),
    ExtractionField.POLICY_NUMBER: re.compile(
        r"\b(?:POL|POLICY)[-\s]?[A-Z0-9]{4,12}\b",
        re.IGNORECASE,
    ),
    ExtractionField.CLAIM_AMOUNT: re.compile(
        r"(?:₹|Rs\.?|INR|\$|USD)\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\b\d{1,3}(?:,\d{3})+\.\d{2}\b",
        re.IGNORECASE,
    ),
    ExtractionField.INVOICE_AMOUNT: re.compile(
        r"(?:₹|Rs\.?|INR|\$|USD)\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\b\d{1,3}(?:,\d{3})+\.\d{2}\b",
        re.IGNORECASE,
    ),
    ExtractionField.INCIDENT_DATE: re.compile(
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
    ),
    ExtractionField.SUBMISSION_DATE: re.compile(
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
    ),
    ExtractionField.VEHICLE_NUMBER: re.compile(
        r"\b[A-Z]{2}\s?\d{1,2}\s?[A-Z]{1,3}\s?\d{1,4}\b",
        re.IGNORECASE,
    ),
}


def normalize_label(text: str) -> str:
    """Normalize a field label for synonym matching."""
    cleaned = text.strip().lower()
    cleaned = cleaned.rstrip(":").strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def match_field_from_label(label: str) -> ExtractionField | None:
    """Map a detected key label to a canonical extraction field."""
    normalized = normalize_label(label)
    if not normalized:
        return None

    for field, synonyms in FIELD_SYNONYMS.items():
        for synonym in synonyms:
            if normalized == synonym or synonym in normalized or normalized in synonym:
                return field
    return None
