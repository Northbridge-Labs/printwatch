"""Jobs repository: ORM access implementing IJobRepository."""
from __future__ import annotations

from typing import Optional
from uuid import uuid4

from apps.jobs.domain.records import JobRecord, PersistedJobRecord
from apps.jobs.infrastructure.models import PrintJob


class DjangoJobRepository:
    def save(
        self,
        record: JobRecord,
        *,
        printer_id: Optional[int],
        user_id: Optional[int],
        cost,
        flags: list,
    ) -> PersistedJobRecord:
        job = PrintJob.objects.create(
            uuid=uuid4(),
            job_type=record.job_type,
            source=record.source,
            user_id=user_id,
            username=record.username,
            printer_id=printer_id,
            printer_name=record.printer_name,
            document_name=record.document_name,
            pages=record.pages,
            copies=record.copies,
            color=record.color,
            duplex=record.duplex,
            submitted_at=record.submitted_at,
            cost=cost,
            raw_payload=record.raw_payload,
            flags=flags,
        )
        return _to_persisted(job)

    def list_recent(self, limit: int = 50) -> list[PersistedJobRecord]:
        qs = PrintJob.objects.select_related("user", "printer").order_by("-captured_at")[:limit]
        return [_to_persisted(j) for j in qs]

    def get_by_id(self, job_id: int) -> Optional[PersistedJobRecord]:
        try:
            j = PrintJob.objects.get(id=job_id)
        except PrintJob.DoesNotExist:
            return None
        return _to_persisted(j)


def _to_persisted(j: PrintJob) -> PersistedJobRecord:
    return PersistedJobRecord(
        id=j.id, uuid=j.uuid, job_type=j.job_type, source=j.source,
        user_id=j.user_id, printer_id=j.printer_id, printer_name=j.printer_name,
        username=j.username, document_name=j.document_name,
        pages=j.pages, copies=j.copies, color=j.color, duplex=j.duplex,
        submitted_at=j.submitted_at, cost=j.cost, flags=list(j.flags),
    )