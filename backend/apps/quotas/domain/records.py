"""Quotas domain records."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class QuotaRuleRecord:
    id: int
    scope: str
    user_id: int | None
    department_id: int | None
    period: str
    page_limit: int
    cost_limit: Decimal
    active_from: str
    active_until: str | None


@dataclass(frozen=True)
class QuotaUsageRecord:
    id: int
    user_id: int
    period_start: str
    period_end: str
    pages_used: int
    cost_used: Decimal
    breached: bool = False