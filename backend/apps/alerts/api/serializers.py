"""Alerts serializers."""
from rest_framework import serializers

from apps.alerts.infrastructure.models import AlertEvent, AlertRule


class AlertRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertRule
        fields = [
            "id", "name", "rule_type", "channel", "target",
            "config", "enabled", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AlertEventSerializer(serializers.ModelSerializer):
    rule_name = serializers.CharField(source="rule.name", read_only=True)

    class Meta:
        model = AlertEvent
        fields = [
            "id", "rule", "rule_name", "user", "printer", "job",
            "message", "payload", "sent_at", "created_at",
        ]
        read_only_fields = fields