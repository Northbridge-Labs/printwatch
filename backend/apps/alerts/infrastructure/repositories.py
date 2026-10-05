"""Alerts repositories."""
from __future__ import annotations

from typing import Optional

from apps.alerts.infrastructure.models import AlertEvent, AlertRule


class DjangoAlertRuleRepository:
    def list_all(self) -> list:
        return list(AlertRule.objects.filter(enabled=True))

    def list_by_type(self, rule_type: str) -> list:
        return list(AlertRule.objects.filter(enabled=True, rule_type=rule_type))

    def create(self, data: dict):
        return AlertRule.objects.create(**data)

    def update(self, rule_id: int, data: dict) -> Optional[AlertRule]:
        try:
            r = AlertRule.objects.get(id=rule_id)
        except AlertRule.DoesNotExist:
            return None
        for k, v in data.items():
            setattr(r, k, v)
        r.save()
        return r

    def delete(self, rule_id: int) -> bool:
        deleted, _ = AlertRule.objects.filter(id=rule_id).delete()
        return bool(deleted)


class DjangoAlertEventRepository:
    def create(self, *, rule_id, user_id, printer_id, job_id, message, payload):
        return AlertEvent.objects.create(
            rule_id=rule_id, user_id=user_id, printer_id=printer_id,
            job_id=job_id, message=message, payload=payload,
        )

    def list_recent(self, limit: int = 50) -> list:
        return list(AlertEvent.objects.select_related("rule", "user", "printer", "job")
                    .order_by("-created_at")[:limit])

    def mark_sent(self, event_id: int) -> None:
        from django.utils import timezone
        AlertEvent.objects.filter(id=event_id).update(sent_at=timezone.now())