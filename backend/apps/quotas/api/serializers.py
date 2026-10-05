"""Quotas serializers."""
from rest_framework import serializers

from apps.quotas.infrastructure.models import QuotaRule, QuotaUsage


class QuotaRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotaRule
        fields = [
            "id", "scope", "user", "department", "period",
            "page_limit", "cost_limit", "active_from", "active_until",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class QuotaUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotaUsage
        fields = [
            "id", "user", "period_start", "period_end",
            "pages_used", "cost_used", "updated_at",
        ]
        read_only_fields = fields