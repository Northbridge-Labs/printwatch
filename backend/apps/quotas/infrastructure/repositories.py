"""Quotas repositories."""
from __future__ import annotations

from typing import Optional

from apps.quotas.domain.records import QuotaRuleRecord, QuotaUsageRecord
from apps.quotas.infrastructure.models import QuotaRule, QuotaUsage


def _to_rule(r: QuotaRule) -> QuotaRuleRecord:
    return QuotaRuleRecord(
        id=r.id, scope=r.scope, user_id=r.user_id, department_id=r.department_id,
        period=r.period, page_limit=r.page_limit, cost_limit=r.cost_limit,
        active_from=r.active_from.isoformat(),
        active_until=r.active_until.isoformat() if r.active_until else None,
    )


def _to_usage(u: QuotaUsage) -> QuotaUsageRecord:
    breached = False
    # Determine breach against the user's most restrictive rule
    rules = QuotaRule.objects.filter(user_id=u.user_id, scope="user")
    for r in rules:
        if r.page_limit and u.pages_used > r.page_limit:
            breached = True
        if r.cost_limit and u.cost_used > r.cost_limit:
            breached = True
    return QuotaUsageRecord(
        id=u.id, user_id=u.user_id,
        period_start=u.period_start.isoformat(),
        period_end=u.period_end.isoformat(),
        pages_used=u.pages_used, cost_used=u.cost_used, breached=breached,
    )


class DjangoQuotaRuleRepository:
    def list_for_user(self, user_id: int) -> list[QuotaRuleRecord]:
        return [_to_rule(r) for r in QuotaRule.objects.filter(user_id=user_id)]

    def list_all(self) -> list[QuotaRuleRecord]:
        return [_to_rule(r) for r in QuotaRule.objects.all()]

    def create(self, data: dict) -> QuotaRuleRecord:
        r = QuotaRule.objects.create(**data)
        return _to_rule(r)

    def update(self, rule_id: int, data: dict) -> Optional[QuotaRuleRecord]:
        try:
            r = QuotaRule.objects.get(id=rule_id)
        except QuotaRule.DoesNotExist:
            return None
        for k, v in data.items():
            setattr(r, k, v)
        r.save()
        return _to_rule(r)

    def delete(self, rule_id: int) -> bool:
        deleted, _ = QuotaRule.objects.filter(id=rule_id).delete()
        return bool(deleted)


class DjangoQuotaUsageRepository:
    def get(self, user_id: int, period_start: str) -> Optional[QuotaUsageRecord]:
        try:
            return _to_usage(QuotaUsage.objects.get(
                user_id=user_id, period_start=period_start
            ))
        except QuotaUsage.DoesNotExist:
            return None

    def save(
        self, user_id: int, period_start, period_end,
        pages_used: int, cost_used,
    ) -> QuotaUsageRecord:
        from datetime import date
        if isinstance(period_start, str):
            period_start = date.fromisoformat(period_start)
        if isinstance(period_end, str):
            period_end = date.fromisoformat(period_end)
        u, _ = QuotaUsage.objects.update_or_create(
            user_id=user_id, period_start=period_start,
            defaults={"period_end": period_end, "pages_used": pages_used,
                      "cost_used": cost_used},
        )
        return _to_usage(u)

    def list_for_user(self, user_id: int) -> list[QuotaUsageRecord]:
        return [_to_usage(u) for u in QuotaUsage.objects.filter(user_id=user_id)]