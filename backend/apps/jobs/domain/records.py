"""Jobs domain records (framework-agnostic)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class JobRecord:
    """Inbound job to be ingested. Carries only what the agent/app sent."""

    job_type: str  # print | scan | copy
    source: str    # cups | windows | api
    printer_name: str
    username: str
    document_name: str
    pages: int
    copies: int = 1
    color: bool = False
    duplex: bool = False
    submitted_at: datetime = None
    raw_payload: dict = field(default_factory=dict)


@dataclass(frozen=True)
class PersistedJobRecord:
    """Job after persistence, with cost + matched entities."""

    id: int
    uuid: UUID
    job_type: str
    source: str
    user_id: Optional[int]
    printer_id: Optional[int]
    printer_name: str
    username: str
    document_name: str
    pages: int
    copies: int
    color: bool
    duplex: bool
    submitted_at: datetime
    cost: Decimal
    flags: list = field(default_factory=list)


@dataclass
class IngestResult:
    """Facade return value."""

    job: PersistedJobRecord
    quota_breached: bool = False
    alert_dispatched: bool = False