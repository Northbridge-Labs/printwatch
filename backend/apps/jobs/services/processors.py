"""Ingestion processors (Strategy + Adapter per source).

Each processor adapts a source-specific wire payload into a unified
``JobRecord``. New sources can be added by registering a new processor — no
modification of existing ones required (OCP).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone


class IngestionProcessor(ABC):
    """Strategy interface."""

    @abstractmethod
    def to_job_record(self, payload: dict) -> "JobRecord":  # noqa: F821
        ...


class CupsProcessor(IngestionProcessor):
    def to_job_record(self, payload: dict):
        from apps.jobs.domain.records import JobRecord
        return JobRecord(
            job_type=payload.get("job_type", "print"),
            source="cups",
            printer_name=payload.get("printer", ""),
            username=payload.get("username", ""),
            document_name=payload.get("document", ""),
            pages=int(payload.get("pages", 0)),
            copies=int(payload.get("copies", 1)),
            color=bool(payload.get("color", False)),
            duplex=bool(payload.get("duplex", False)),
            submitted_at=datetime.fromisoformat(payload["submitted_at"])
            if "submitted_at" in payload else datetime.now(timezone.utc),
            raw_payload=payload.get("raw", {}),
        )


class WindowsProcessor(IngestionProcessor):
    def to_job_record(self, payload: dict):
        # Windows payload uses the same shape as CUPS via the agent's JSONL.
        rec = CupsProcessor().to_job_record(payload)
        from dataclasses import replace
        return replace(rec, source="windows")


class ApiProcessor(IngestionProcessor):
    """Used by the public /api/v1/jobs/log endpoint (third-party apps)."""

    def to_job_record(self, payload: dict):
        rec = CupsProcessor().to_job_record(payload)
        from dataclasses import replace
        return replace(rec, source="api")


class IngestionProcessorFactory:
    _processors: dict[str, IngestionProcessor] = {
        "cups": CupsProcessor(),
        "windows": WindowsProcessor(),
        "api": ApiProcessor(),
    }

    @classmethod
    def get(cls, source: str) -> IngestionProcessor:
        processor = cls._processors.get(source)
        if processor is None:
            raise ValueError(f"Unknown source: {source}")
        return processor

    @classmethod
    def register(cls, source: str, processor: IngestionProcessor) -> None:
        cls._processors[source] = processor