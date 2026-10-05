"""Reporting services: read-only aggregations.

No ORM models; uses the jobs/printers repositories or direct queryset
aggregations cached in Valkey for 5 minutes, keyed by query hash + role scope.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date, timedelta
from typing import Optional

from django.core.cache import cache


class ReportingService:
    """Aggregate report builders. All results cached 5 min."""

    CACHE_TTL = 300

    def __init__(self) -> None:
        pass

    def _cached(self, key_parts: dict, compute):
        key = "report:" + hashlib.sha256(
            json.dumps(key_parts, sort_keys=True, default=str).encode()
        ).hexdigest()
        cached = cache.get(key)
        if cached is not None:
            return cached
        result = compute()
        cache.set(key, result, self.CACHE_TTL)
        return result

    def summary(self, start: Optional[date] = None, end: Optional[date] = None) -> dict:
        end = end or date.today()
        start = start or (end - timedelta(days=30))

        def compute():
            from apps.jobs.infrastructure.models import PrintJob
            from django.db.models import Sum, Count
            qs = PrintJob.objects.filter(submitted_at__date__range=(start, end))
            agg = qs.aggregate(
                total=Count("id"),
                pages=Sum("pages"),
                cost=Sum("cost"),
            )
            by_type = list(
                qs.values("job_type").annotate(
                    pages=Sum("pages"), cost=Sum("cost"), count=Count("id"),
                ).order_by("job_type")
            )
            return {
                "range": {"start": start.isoformat(), "end": end.isoformat()},
                "total_jobs": agg["total"] or 0,
                "total_pages": agg["pages"] or 0,
                "total_cost": str(agg["cost"] or 0),
                "by_type": by_type,
            }

        return self._cached({"fn": "summary", "start": start, "end": end}, compute)

    def pages_by_user(self, start: date, end: date, job_type: Optional[str] = None) -> list:
        def compute():
            from apps.jobs.infrastructure.models import PrintJob
            from django.db.models import Sum
            qs = PrintJob.objects.filter(submitted_at__date__range=(start, end))
            if job_type:
                qs = qs.filter(job_type=job_type)
            return list(
                qs.values("user__email").annotate(
                    pages=Sum("pages"), cost=Sum("cost"),
                ).order_by("-pages")[:50]
            )

        return self._cached(
            {"fn": "pages_by_user", "start": start, "end": end, "type": job_type},
            compute,
        )

    def pages_by_printer(self, start: date, end: date, job_type: Optional[str] = None) -> list:
        def compute():
            from apps.jobs.infrastructure.models import PrintJob
            from django.db.models import Sum
            qs = PrintJob.objects.filter(submitted_at__date__range=(start, end))
            if job_type:
                qs = qs.filter(job_type=job_type)
            return list(
                qs.values("printer__name").annotate(
                    pages=Sum("pages"), cost=Sum("cost"),
                ).order_by("-pages")[:50]
            )

        return self._cached(
            {"fn": "pages_by_printer", "start": start, "end": end, "type": job_type},
            compute,
        )

    def jobs_by_type(self, start: date, end: date) -> list:
        def compute():
            from apps.jobs.infrastructure.models import PrintJob
            from django.db.models import Count
            return list(
                PrintJob.objects.filter(submitted_at__date__range=(start, end))
                .values("job_type").annotate(count=Count("id")).order_by("job_type")
            )

        return self._cached(
            {"fn": "jobs_by_type", "start": start, "end": end}, compute
        )

    def cost_trend(self, start: date, end: date, job_type: Optional[str] = None) -> list:
        def compute():
            from apps.jobs.infrastructure.models import PrintJob
            from django.db.models import Sum
            from django.db.models.functions import TruncDate
            qs = PrintJob.objects.filter(submitted_at__date__range=(start, end))
            if job_type:
                qs = qs.filter(job_type=job_type)
            return list(
                qs.annotate(day=TruncDate("submitted_at"))
                .values("day").annotate(cost=Sum("cost"), pages=Sum("pages"))
                .order_by("day")
            )

        return self._cached(
            {"fn": "cost_trend", "start": start, "end": end, "type": job_type},
            compute,
        )