"""Alerts views."""
from drf_spectacular.utils import extend_schema
from rest_framework import generics

from apps.accounts.api.permissions import IsOperatorOrAdmin

from .serializers import AlertEventSerializer, AlertRuleSerializer


@extend_schema(tags=["Alerts"])
class AlertRuleListCreateView(generics.ListCreateAPIView):
    serializer_class = AlertRuleSerializer
    permission_classes = [IsOperatorOrAdmin]

    def get_queryset(self):
        from apps.alerts.infrastructure.models import AlertRule
        return AlertRule.objects.all()


@extend_schema(tags=["Alerts"])
class AlertRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AlertRuleSerializer
    permission_classes = [IsOperatorOrAdmin]
    lookup_url_kwarg = "rule_id"

    def get_queryset(self):
        from apps.alerts.infrastructure.models import AlertRule
        return AlertRule.objects.all()


@extend_schema(tags=["Alerts"])
class AlertEventListView(generics.ListAPIView):
    serializer_class = AlertEventSerializer
    permission_classes = [IsOperatorOrAdmin]

    def get_queryset(self):
        from apps.alerts.infrastructure.models import AlertEvent
        return AlertEvent.objects.select_related("rule", "user", "printer", "job").all()