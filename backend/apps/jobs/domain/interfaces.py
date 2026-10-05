"""Jobs domain interfaces."""
from __future__ import annotations

from typing import Optional, Protocol

from .records import IngestResult, JobRecord, PersistedJobRecord


class IJobRepository(Protocol):
    def save(self, record: JobRecord, *, printer_id: Optional[int],
             user_id: Optional[int], cost, flags: list) -> PersistedJobRecord: ...
    def list_recent(self, limit: int = 50) -> list[PersistedJobRecord]: ...
    def get_by_id(self, job_id: int) -> Optional[PersistedJobRecord]: ...


class ICostCalculator(Protocol):
    def calculate(self, job: JobRecord, printer) -> float: ...
    """Returns the cost for a job given the printer record."""


class IJobIngestionFacade(Protocol):
    def ingest(self, record: JobRecord) -> IngestResult: ...