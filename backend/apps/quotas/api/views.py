"""Quotas views."""
from drf_spectacular.utils import extend_schema
from rest_framework import generics

from apps.accounts.api.permissions import IsOperatorOrAdmin

from .serializers import QuotaRuleSerializer, QuotaUsageSerializer


@extend_schema(tags=["Quotas"])
class QuotaRuleListCreateView(generics.ListCreateAPIView):
    serializer_class = QuotaRuleSerializer
    permission_classes = [IsOperatorOrAdmin]

    def get_queryset(self):
        from apps.quotas.infrastructure.models import QuotaRule
        return QuotaRule.objects.all()


@extend_schema(tags=["Quotas"])
class QuotaRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QuotaRuleSerializer
    permission_classes = [IsOperatorOrAdmin]
    lookup_url_kwarg = "rule_id"

    def get_queryset(self):
        from apps.quotas.infrastructure.models import QuotaRule
        return QuotaRule.objects.all()


@extend_schema(tags=["Quotas"])
class QuotaUsageListView(generics.ListAPIView):
    serializer_class = QuotaUsageSerializer
    permission_classes = [IsOperatorOrAdmin]

    def get_queryset(self):
        from apps.quotas.infrastructure.models import QuotaUsage
        qs = QuotaUsage.objects.all()
        user_id = self.request.query_params.get("user")
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs