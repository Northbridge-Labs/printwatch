"""Quotas admin registration."""
from django.contrib import admin

from apps.quotas.infrastructure.models import QuotaRule, QuotaUsage


@admin.register(QuotaRule)
class QuotaRuleAdmin(admin.ModelAdmin):
    list_display = ("scope", "user", "department", "period",
                    "page_limit", "cost_limit", "active_from")
    list_filter = ("scope", "period")
    search_fields = ("user__email", "department__name")


@admin.register(QuotaUsage)
class QuotaUsageAdmin(admin.ModelAdmin):
    list_display = ("user", "period_start", "period_end",
                    "pages_used", "cost_used", "updated_at")
    list_filter = ("period_start",)
    search_fields = ("user__email",)