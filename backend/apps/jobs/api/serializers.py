"""Jobs serializers."""
from rest_framework import serializers

from apps.jobs.infrastructure.models import PrintJob


class PrintJobSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = PrintJob
        fields = [
            "id", "uuid", "job_type", "source", "user", "user_email",
            "username", "printer", "printer_name", "document_name",
            "pages", "copies", "color", "duplex", "submitted_at",
            "captured_at", "cost", "flags", "raw_payload",
        ]
        read_only_fields = ["id", "uuid", "captured_at", "cost", "flags"]

    def get_user_email(self, obj):
        return obj.user.email if obj.user else None


class JobLogRequestSerializer(serializers.Serializer):
    """Public developer API request body (documented in Swagger)."""

    job_type = serializers.ChoiceField(
        choices=["print", "scan", "copy"], default="print"
    )
    printer = serializers.CharField(max_length=128)
    username = serializers.CharField(max_length=150)
    document_name = serializers.CharField(max_length=255, required=False,
                                           allow_blank=True)
    pages = serializers.IntegerField(min_value=0)
    copies = serializers.IntegerField(min_value=1, default=1)
    color = serializers.BooleanField(default=False)
    duplex = serializers.BooleanField(default=False)
    submitted_at = serializers.DateTimeField()


class JobLogResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    uuid = serializers.UUIDField()
    cost = serializers.DecimalField(max_digits=12, decimal_places=4)
    flags = serializers.ListField(child=serializers.CharField())