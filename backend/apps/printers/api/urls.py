"""Printers URL routes."""
from django.urls import path

from .views import (
    DepartmentDetailView,
    DepartmentListCreateView,
    PrinterDetailView,
    PrinterListCreateView,
)

urlpatterns = [
    path("printers", PrinterListCreateView.as_view(), name="printer-list"),
    path("printers/<int:printer_id>", PrinterDetailView.as_view(), name="printer-detail"),
    path("departments", DepartmentListCreateView.as_view(), name="department-list"),
    path("departments/<int:department_id>", DepartmentDetailView.as_view(), name="department-detail"),
]