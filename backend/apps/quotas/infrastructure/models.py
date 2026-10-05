"""Quotas ORM models."""
from django.db import models


class QuotaRule(models.Model):
    class Scope(models.TextChoices):
        USER = "user", "User"
        DEPARTMENT = "department", "Department"

    class Period(models.TextChoices):
        DAILY = "daily", "Daily"
        MONTHLY = "monthly", "Monthly"

    scope = models.CharField(max_length=16, choices=Scope.choices)
    user = models.ForeignKey(
        "accounts.User", null=True, blank=True,
        on_delete=models.CASCADE, related_name="quota_rules",
    )
    department = models.ForeignKey(
        "printers.Department", null=True, blank=True,
        on_delete=models.CASCADE, related_name="quota_rules",
    )
    period = models.CharField(max_length=16, choices=Period.choices)
    page_limit = models.PositiveIntegerField(default=0)
    cost_limit = models.DecimalField(
        max_digits=12, decimal_places=4, default=0
    )
    active_from = models.DateField()
    active_until = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(scope="user", user__isnull=False)
                    | models.Q(scope="department", department__isnull=False)
                ),
                name="quota_rule_must_have_target",
            ),
        ]

    def __str__(self) -> str:
        target = self.user.email if self.user else self.department.name
        return f"{self.scope}:{target} {self.period}"


class QuotaUsage(models.Model):
    """Snapshot of usage per user/period. Recomputed by Celery."""

    user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="quota_usages"
    )
    period_start = models.DateField()
    period_end = models.DateField()
    pages_used = models.PositiveIntegerField(default=0)
    cost_used = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "period_start"]
        ordering = ["-period_start"]