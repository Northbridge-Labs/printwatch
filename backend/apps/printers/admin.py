"""Printers admin registration."""
from django.contrib import admin

from apps.printers.infrastructure.models import Department, Printer


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at")
    search_fields = ("name",)


@admin.register(Printer)
class PrinterAdmin(admin.ModelAdmin):
    list_display = ("name", "model", "host", "status", "department")
    list_filter = ("status", "department")
    search_fields = ("name", "host", "model")