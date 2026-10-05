"""Post-ingest pipeline: Chain of Responsibility.

Each step receives the persisted job and a shared :class:`PipelineContext`,
performs its concern, and calls ``next_step`` (or short-circuits). New steps
can be inserted without modifying existing ones (OCP).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from apps.jobs.domain.records import IngestResult, PersistedJobRecord


@dataclass
class PipelineContext:
    job: PersistedJobRecord
    result: IngestResult
    extras: dict = field(default_factory=dict)


class PipelineStep:
    """Abstract handler."""

    def __init__(self) -> None:
        self._next: Optional[PipelineStep] = None

    def set_next(self, step: "PipelineStep") -> "PipelineStep":
        self._next = step
        return step

    def handle(self, ctx: PipelineContext) -> PipelineContext:
        if self._next is not None:
            return self._next.handle(ctx)
        return ctx


class QuotaCheckStep(PipelineStep):
    """Calls the quota service to evaluate usage against limits.

    Implemented as a thin wrapper that dispatches a Celery task so the facade
    stays fast and the quota evaluation is idempotent + retryable.
    """

    def handle(self, ctx: PipelineContext) -> PipelineContext:
        if ctx.job.job_type in ("print", "copy") and ctx.job.user_id:
            from apps.quotas.tasks import evaluate_quota_for_job
            evaluate_quota_for_job.delay(ctx.job.id, ctx.job.user_id)
            # We can't know the result synchronously without blocking; the
            # task updates the job's flags asynchronously. Mark as dispatched.
            ctx.result.quota_breached = False
            ctx.extras["quota_task_dispatched"] = True
        return super().handle(ctx)


class AlertEvaluateStep(PipelineStep):
    """Dispatches an async alert evaluation Celery task."""

    def handle(self, ctx: PipelineContext) -> PipelineContext:
        from apps.alerts.tasks import evaluate_alerts_for_job
        evaluate_alerts_for_job.delay(ctx.job.id)
        ctx.result.alert_dispatched = True
        return super().handle(ctx)


def build_default_pipeline() -> PipelineStep:
    """Builds the standard chain: quota → alert."""
    quota = QuotaCheckStep()
    quota.set_next(AlertEvaluateStep())
    return quota