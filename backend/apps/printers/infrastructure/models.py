"""Printers ORM models."""
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Printer(models.Model):
    class Status(models.TextChoices):
        ONLINE = "online", "Online"
        OFFLINE = "offline", "Offline"
        ERROR = "error", "Error"
        UNKNOWN = "unknown", "Unknown"

    name = models.CharField(max_length=128, unique=True)
    host = models.CharField(max_length=255, blank=True)
    model = models.CharField(max_length=128, blank=True)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.UNKNOWN
    )
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="printers",
    )
    cost_per_page_bw = models.DecimalField(
        max_digits=8, decimal_places=4, default=0
    )
    cost_per_page_color = models.DecimalField(
        max_digits=8, decimal_places=4, default=0
    )
    scan_cost_per_page = models.DecimalField(
        max_digits=8, decimal_places=4, default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name