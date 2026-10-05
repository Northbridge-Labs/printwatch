"""Quotas Celery tasks (Command pattern)."""
from __future__ import annotations

from celery import shared_task


@shared_task(bind=True)
def evaluate_quota_for_job(self, job_id: int, user_id: int) -> bool:
    """Recompute quota usage for the user owning ``job_id`` and update flags."""
    from apps.common.container import container
    from apps.jobs.infrastructure.models import PrintJob

    try:
        job = PrintJob.objects.get(id=job_id)
    except PrintJob.DoesNotExist:
        return False

    quota_service = container.resolve("quota_service")
    breached = quota_service.evaluate_for_job(user_id, job.submitted_at)
    if breached:
        job.flags = list(set(job.flags + ["quota_breached"]))
        job.save(update_fields=["flags"])
    return breached


@shared_task
def recompute_all_quotas() -> None:
    """Beat task: recompute usage for every active user."""
    from apps.accounts.infrastructure.models import User
    from apps.common.container import container

    quota_service = container.resolve("quota_service")
    for user in User.objects.filter(is_active=True):
        quota_service.compute_usage(user.id)