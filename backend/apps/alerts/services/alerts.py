"""Alerts service: evaluates rules and dispatches notifications."""
from __future__ import annotations

from typing import Optional


class AlertService:
    def __init__(self, rules_repo, events_repo, dispatcher) -> None:
        self._rules = rules_repo
        self._events = events_repo
        self._dispatcher = dispatcher

    def list_rules(self) -> list:
        return self._rules.list_all()

    def create_rule(self, data: dict):
        return self._rules.create(data)

    def update_rule(self, rule_id: int, data: dict):
        return self._rules.update(rule_id, data)

    def delete_rule(self, rule_id: int) -> bool:
        return self._rules.delete(rule_id)

    def list_events(self) -> list:
        return self._events.list_recent()

    def evaluate_job(self, job_id: int, breached: bool) -> Optional[int]:
        """Create + dispatch an alert event if a quota-breach rule matches."""
        if not breached:
            return None
        rules = self._rules.list_by_type("quota_breach")
        if not rules:
            return None
        from apps.jobs.infrastructure.models import PrintJob
        try:
            job = PrintJob.objects.get(id=job_id)
        except PrintJob.DoesNotExist:
            return None
        event_ids = []
        for rule in rules:
            event = self._events.create(
                rule_id=rule.id,
                user_id=job.user_id,
                printer_id=job.printer_id,
                job_id=job.id,
                message=f"Quota breached by {job.username}",
                payload={"pages": job.pages, "cost": str(job.cost)},
            )
            self._dispatcher.send(rule, event)
            event_ids.append(event.id)
        return event_ids[0] if event_ids else None