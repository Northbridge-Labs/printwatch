"""Jobs ORM models."""
from django.db import models


class PrintJob(models.Model):
    class JobType(models.TextChoices):
        PRINT = "print", "Print"
        SCAN = "scan", "Scan"
        COPY = "copy", "Copy"

    class Source(models.TextChoices):
        CUPS = "cups", "CUPS filter"
        WINDOWS = "windows", "Windows agent"
        API = "api", "Developer API"

    uuid = models.UUIDField(db_index=True, unique=True, editable=False)
    job_type = models.CharField(
        max_length=8, choices=JobType.choices, default=JobType.PRINT
    )
    user = models.ForeignKey(
        "accounts.User", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="print_jobs",
    )
    username = models.CharField(max_length=150)
    printer = models.ForeignKey(
        "printers.Printer", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="jobs",
    )
    printer_name = models.CharField(max_length=128, blank=True)
    document_name = models.CharField(max_length=255, blank=True)
    pages = models.PositiveIntegerField(default=0)
    copies = models.PositiveIntegerField(default=1)
    color = models.BooleanField(default=False)
    duplex = models.BooleanField(default=False)
    submitted_at = models.DateTimeField()
    captured_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=16, choices=Source.choices)
    cost = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    raw_payload = models.JSONField(default=dict, blank=True)
    flags = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["-captured_at"]
        indexes = [
            models.Index(fields=["-captured_at"]),
            models.Index(fields=["job_type"]),
            models.Index(fields=["source"]),
            models.Index(fields=["user"]),
            models.Index(fields=["printer"]),
        ]

    def __str__(self) -> str:
        return f"Job {self.uuid} ({self.job_type})"