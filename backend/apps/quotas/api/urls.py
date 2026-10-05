"""Quotas URL routes."""
from django.urls import path

from .views import (
    QuotaRuleDetailView,
    QuotaRuleListCreateView,
    QuotaUsageListView,
)

urlpatterns = [
    path("quotas/rules", QuotaRuleListCreateView.as_view(), name="quota-rule-list"),
    path("quotas/rules/<int:rule_id>", QuotaRuleDetailView.as_view(), name="quota-rule-detail"),
    path("quotas/usage", QuotaUsageListView.as_view(), name="quota-usage-list"),
]