"""Printers views: thin, delegate to service via DI container."""
from drf_spectacular.utils import extend_schema
from rest_framework import generics

from apps.accounts.api.permissions import IsOperatorOrAdmin

from .serializers import DepartmentSerializer, PrinterSerializer


@extend_schema(tags=["Printers"])
class PrinterListCreateView(generics.ListCreateAPIView):
    serializer_class = PrinterSerializer
    permission_classes = [IsOperatorOrAdmin]

    def get_queryset(self):
        from apps.printers.infrastructure.models import Printer
        return Printer.objects.all()


@extend_schema(tags=["Printers"])
class PrinterDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PrinterSerializer
    permission_classes = [IsOperatorOrAdmin]
    lookup_url_kwarg = "printer_id"

    def get_queryset(self):
        from apps.printers.infrastructure.models import Printer
        return Printer.objects.all()


@extend_schema(tags=["Printers"])
class DepartmentListCreateView(generics.ListCreateAPIView):
    serializer_class = DepartmentSerializer
    permission_classes = [IsOperatorOrAdmin]

    def get_queryset(self):
        from apps.printers.infrastructure.models import Department
        return Department.objects.all()


@extend_schema(tags=["Printers"])
class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DepartmentSerializer
    permission_classes = [IsOperatorOrAdmin]
    lookup_url_kwarg = "department_id"

    def get_queryset(self):
        from apps.printers.infrastructure.models import Department
        return Department.objects.all()