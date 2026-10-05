"""Jobs admin registration."""
from django.contrib import admin

from apps.jobs.infrastructure.models import PrintJob


@admin.register(PrintJob)
class PrintJobAdmin(admin.ModelAdmin):
    list_display = (
        "uuid", "job_type", "source", "username", "printer",
        "pages", "cost", "submitted_at",
    )
    list_filter = ("job_type", "source", "color", "printer")
    search_fields = ("username", "document_name", "printer_name")
    date_hierarchy = "submitted_at"
    ordering = ("-submitted_at",)