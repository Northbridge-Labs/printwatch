"""Alerts Celery tasks."""
from __future__ import annotations

from celery import shared_task


@shared_task
def evaluate_alerts_for_job(job_id: int) -> None:
    """Evaluate alert rules for a freshly ingested job."""
    from apps.common.container import container
    from apps.jobs.infrastructure.models import PrintJob

    try:
        job = PrintJob.objects.get(id=job_id)
    except PrintJob.DoesNotExist:
        return
    breached = "quota_breached" in (job.flags or [])
    svc = container.resolve("alert_service")
    svc.evaluate_job(job_id, breached)


@shared_task
def check_printer_status() -> None:
    """Beat task: scan printers and emit offline alerts."""
    from apps.printers.infrastructure.models import Printer
    from apps.alerts.infrastructure.models import AlertRule, AlertEvent
    rules = AlertRule.objects.filter(enabled=True, rule_type="printer_offline")
    for printer in Printer.objects.filter(status="offline"):
        for rule in rules:
            AlertEvent.objects.create(
                rule=rule, printer=printer,
                message=f"Printer {printer.name} offline",
                payload={"printer_id": printer.id},
            )