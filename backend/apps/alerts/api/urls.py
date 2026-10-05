"""Alerts URL routes."""
from django.urls import path

from .views import (
    AlertEventListView,
    AlertRuleDetailView,
    AlertRuleListCreateView,
)

urlpatterns = [
    path("alerts/rules", AlertRuleListCreateView.as_view(), name="alert-rule-list"),
    path("alerts/rules/<int:rule_id>", AlertRuleDetailView.as_view(), name="alert-rule-detail"),
    path("alerts/events", AlertEventListView.as_view(), name="alert-event-list"),
]