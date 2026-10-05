"""Printers serializers."""
from rest_framework import serializers

from apps.printers.infrastructure.models import Department, Printer


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "description", "created_at"]
        read_only_fields = ["id", "created_at"]


class PrinterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Printer
        fields = [
            "id", "name", "host", "model", "status", "department",
            "cost_per_page_bw", "cost_per_page_color", "scan_cost_per_page",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]