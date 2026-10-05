"""Quotas service: business logic over repositories.

The service is framework-agnostic: it receives dataclasses and uses injected
repositories. It computes usage by querying jobs aggregated from the jobs app
via a repository interface (kept here as a port to avoid importing the ORM).
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from apps.quotas.domain.interfaces import (
    IQuotaRuleRepository, IQuotaUsageRepository,
)
from apps.quotas.domain.records import QuotaRuleRecord, QuotaUsageRecord


class QuotaService:
    """Computes and persists per-user quota usage."""

    def __init__(
        self,
        rules: IQuotaRuleRepository,
        usages: IQuotaUsageRepository,
        jobs_aggregator,
    ) -> None:
        self._rules = rules
        self._usages = usages
        self._jobs_aggregator = jobs_aggregator

    def list_rules(self, user_id: Optional[int] = None) -> list[QuotaRuleRecord]:
        if user_id is None:
            return self._rules.list_all()
        return self._rules.list_for_user(user_id)

    def create_rule(self, data: dict) -> QuotaRuleRecord:
        return self._rules.create(data)

    def update_rule(self, rule_id: int, data: dict):
        return self._rules.update(rule_id, data)

    def delete_rule(self, rule_id: int) -> bool:
        return self._rules.delete(rule_id)

    def compute_usage(self, user_id: int, day: Optional[date] = None) -> QuotaUsageRecord:
        """Compute usage for the period containing ``day`` (default: today)."""
        day = day or date.today()
        period_start, period_end = self._period_bounds(day)
        agg = self._jobs_aggregator.aggregate(user_id, period_start, period_end)
        return self._usages.save(
            user_id=user_id,
            period_start=period_start.isoformat(),
            period_end=period_end.isoformat(),
            pages_used=agg["pages"],
            cost_used=agg["cost"],
        )

    def evaluate_for_job(self, user_id: int, submitted_at) -> bool:
        """Recompute usage and return whether any quota is breached."""
        day = submitted_at.date() if hasattr(submitted_at, "date") else submitted_at
        usage = self.compute_usage(user_id, day)
        return usage.breached

    @staticmethod
    def _period_bounds(day: date) -> tuple[date, date]:
        start = day.replace(day=1)
        end = (start + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        return start, end