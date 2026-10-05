"""Unit tests for the post-ingest pipeline (Chain of Responsibility)."""
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from apps.jobs.domain.records import IngestResult, PersistedJobRecord
from apps.jobs.services.pipeline import (
    AlertEvaluateStep,
    PipelineContext,
    PipelineStep,
    QuotaCheckStep,
    build_default_pipeline,
)


def _job(job_type="print", user_id=1):
    return PersistedJobRecord(
        id=1, uuid=uuid4(), job_type=job_type, source="api",
        user_id=user_id, printer_id=1, printer_name="HP",
        username="jdoe", document_name="x", pages=2, copies=1,
        color=False, duplex=False, submitted_at=datetime(2026, 1, 1),
        cost=Decimal("0.20"), flags=[],
    )


def test_pipeline_passes_through_without_steps():
    step = PipelineStep()
    ctx = PipelineContext(job=_job(), result=IngestResult(job=_job()))
    assert step.handle(ctx) is ctx


def test_quota_step_skips_scan_jobs():
    step = QuotaCheckStep()
    ctx = PipelineContext(job=_job("scan"), result=IngestResult(job=_job("scan")))
    step.handle(ctx)
    assert ctx.extras.get("quota_task_dispatched") is None


def test_quota_step_dispatches_for_print():
    from apps.quotas import tasks as quotas_tasks
    from apps.jobs.services import pipeline as pipeline_mod

    dispatched = {}

    class FakeTask:
        def delay(self, job_id, user_id):
            dispatched["called"] = True
            return True

    original = quotas_tasks.evaluate_quota_for_job
    quotas_tasks.evaluate_quota_for_job = FakeTask()  # type: ignore[assignment]
    pipeline_mod.evaluate_quota_for_job = quotas_tasks.evaluate_quota_for_job  # type: ignore[attr-defined]
    try:
        step = QuotaCheckStep()
        ctx = PipelineContext(job=_job("print"), result=IngestResult(job=_job("print")))
        step.handle(ctx)
        assert dispatched.get("called") is True
    finally:
        quotas_tasks.evaluate_quota_for_job = original  # type: ignore[assignment]
        pipeline_mod.evaluate_quota_for_job = original  # type: ignore[attr-defined]


def test_build_default_pipeline_chains_quota_then_alert():
    head = build_default_pipeline()
    assert isinstance(head, QuotaCheckStep)
    assert isinstance(head._next, AlertEvaluateStep)
    assert head._next._next is None