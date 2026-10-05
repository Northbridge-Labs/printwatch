"""Reporting URL routes."""
from django.urls import path

from .views import (
    CostTrendView,
    JobsByTypeView,
    PagesByPrinterView,
    PagesByUserView,
    SummaryView,
)

urlpatterns = [
    path("reporting/summary", SummaryView.as_view(), name="reporting-summary"),
    path("reporting/pages-by-user", PagesByUserView.as_view(), name="reporting-pages-by-user"),
    path("reporting/pages-by-printer", PagesByPrinterView.as_view(), name="reporting-pages-by-printer"),
    path("reporting/jobs-by-type", JobsByTypeView.as_view(), name="reporting-jobs-by-type"),
    path("reporting/cost-trend", CostTrendView.as_view(), name="reporting-cost-trend"),
]