"""Alerts ORM models."""
from django.db import models


class AlertRule(models.Model):
    class Type(models.TextChoices):
        QUOTA_BREACH = "quota_breach", "Quota breach"
        PRINTER_OFFLINE = "printer_offline", "Printer offline"
        COST_THRESHOLD = "cost_threshold", "Cost threshold"

    class Channel(models.TextChoices):
        EMAIL = "email", "Email"
        WEBHOOK = "webhook", "Webhook"

    name = models.CharField(max_length=128)
    rule_type = models.CharField(max_length=32, choices=Type.choices)
    channel = models.CharField(max_length=16, choices=Channel.choices,
                                default=Channel.EMAIL)
    target = models.CharField(max_length=255, blank=True,
                               help_text="Email address or webhook URL")
    config = models.JSONField(default=dict, blank=True)
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


class AlertEvent(models.Model):
    rule = models.ForeignKey(
        AlertRule, on_delete=models.CASCADE, related_name="events"
    )
    user = models.ForeignKey(
        "accounts.User", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="alert_events",
    )
    printer = models.ForeignKey(
        "printers.Printer", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="alert_events",
    )
    job = models.ForeignKey(
        "jobs.PrintJob", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="alert_events",
    )
    message = models.TextField()
    payload = models.JSONField(default=dict, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]