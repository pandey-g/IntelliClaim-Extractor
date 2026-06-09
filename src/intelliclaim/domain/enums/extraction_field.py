"""Insurance claim field identifiers for structured extraction."""

from enum import StrEnum


class ExtractionField(StrEnum):
    """Canonical field names extracted from insurance claim documents."""

    CLAIM_ID = "claim_id"
    POLICY_NUMBER = "policy_number"
    INSURED_NAME = "insured_name"
    CLAIMANT_NAME = "claimant_name"
    ADDRESS = "address"
    CLAIM_AMOUNT = "claim_amount"
    INVOICE_AMOUNT = "invoice_amount"
    HOSPITAL_NAME = "hospital_name"
    VEHICLE_NUMBER = "vehicle_number"
    INCIDENT_DATE = "incident_date"
    SUBMISSION_DATE = "submission_date"
