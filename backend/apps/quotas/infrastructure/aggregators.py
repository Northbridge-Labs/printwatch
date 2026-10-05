"""Jobs aggregator: queries the jobs table for quota computation.

Implements the port used by :class:`QuotaService`. Kept in the quotas
infrastructure layer because it touches the jobs ORM directly (cross-app read).
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal


class DjangoJobsAggregator:
    def aggregate(self, user_id: int, period_start: date, period_end: date) -> dict:
        from apps.jobs.infrastructure.models import PrintJob
        from django.db.models import Sum

        qs = PrintJob.objects.filter(
            user_id=user_id,
            job_type__in=("print", "copy"),
            submitted_at__date__gte=period_start,
            submitted_at__date__lte=period_end,
        )
        agg = qs.aggregate(
            pages=Sum("pages"), cost=Sum("cost"),
        )
        return {
            "pages": agg["pages"] or 0,
            "cost": Decimal(agg["cost"] or 0),
        }