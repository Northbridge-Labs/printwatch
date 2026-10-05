"""Unit tests for ingestion processors (Adapter pattern)."""
from datetime import datetime

from apps.jobs.services.processors import (
    ApiProcessor,
    CupsProcessor,
    IngestionProcessorFactory,
    WindowsProcessor,
)


def test_cups_processor_translates_payload():
    payload = {
        "printer": "HP-LJ", "username": "jdoe", "document": "x.pdf",
        "pages": 5, "copies": 2, "color": True, "duplex": False,
        "submitted_at": "2026-07-27T10:00:00", "raw": {"k": 1},
    }
    rec = CupsProcessor().to_job_record(payload)
    assert rec.source == "cups"
    assert rec.printer_name == "HP-LJ"
    assert rec.pages == 5
    assert rec.copies == 2
    assert rec.color is True
    assert rec.raw_payload == {"k": 1}


def test_windows_processor_sets_source():
    rec = WindowsProcessor().to_job_record({"printer": "p", "username": "u"})
    assert rec.source == "windows"


def test_api_processor_sets_source():
    rec = ApiProcessor().to_job_record({"printer": "p", "username": "u"})
    assert rec.source == "api"


def test_factory_resolves_by_source():
    assert isinstance(IngestionProcessorFactory.get("cups"), CupsProcessor)
    assert isinstance(IngestionProcessorFactory.get("windows"), WindowsProcessor)
    assert isinstance(IngestionProcessorFactory.get("api"), ApiProcessor)


def test_factory_register_extends_sources():
    class CustomProc(CupsProcessor):
        pass
    IngestionProcessorFactory.register("custom", CustomProc())
    assert isinstance(IngestionProcessorFactory.get("custom"), CustomProc)