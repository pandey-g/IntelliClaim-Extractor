"""Background processing job states."""

from enum import StrEnum


class JobStatus(StrEnum):
    """Represents the state of an asynchronous processing job."""

    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    RETRYING = "retrying"
