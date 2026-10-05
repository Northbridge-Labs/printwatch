"""Alerts admin registration."""
from django.contrib import admin

from apps.alerts.infrastructure.models import AlertEvent, AlertRule


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "rule_type", "channel", "target", "enabled")
    list_filter = ("rule_type", "channel", "enabled")
    search_fields = ("name", "target")


@admin.register(AlertEvent)
class AlertEventAdmin(admin.ModelAdmin):
    list_display = ("rule", "user", "printer", "job", "sent_at", "created_at")
    list_filter = ("rule__rule_type", "created_at")
    search_fields = ("message",)