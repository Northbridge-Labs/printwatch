"""Jobs views."""
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from apps.common.container import container

from .serializers import (
    JobLogRequestSerializer,
    PrintJobSerializer,
)


@extend_schema(tags=["Jobs"], responses=PrintJobSerializer)
class JobListCreateView(generics.ListAPIView):
    """List recent jobs (admin/operator). Read-only via this endpoint."""

    serializer_class = PrintJobSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from apps.jobs.infrastructure.models import PrintJob
        return PrintJob.objects.select_related("user", "printer").all()


@extend_schema(tags=["Jobs"], responses=PrintJobSerializer)
class JobDetailView(generics.RetrieveAPIView):
    serializer_class = PrintJobSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = "job_id"

    def get_queryset(self):
        from apps.jobs.infrastructure.models import PrintJob
        return PrintJob.objects.all()


@extend_schema(
    tags=["Developer API"],
    request=JobLogRequestSerializer,
    responses={
        201: OpenApiExample(
            "Job logged",
            value={"id": 1, "uuid": "...", "cost": "0.40", "flags": []},
        )
    },
    description="Log a print/scan/copy job from a third-party printer app. "
                "Authenticated with a long-lived developer JWT (Bearer header).",
)
class JobLogView(APIView):
    """Public developer endpoint, throttled per user."""

    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def post(self, request):
        serializer = JobLogRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        from apps.jobs.services.processors import ApiProcessor

        processor = ApiProcessor()
        record = processor.to_job_record({
            "job_type": data["job_type"],
            "printer": data["printer"],
            "username": data["username"],
            "document": data.get("document_name", ""),
            "pages": data["pages"],
            "copies": data["copies"],
            "color": data["color"],
            "duplex": data["duplex"],
            "submitted_at": data["submitted_at"].isoformat(),
            "raw": {},
        })

        facade = container.resolve("job_ingestion_facade")
        result = facade.ingest(record)
        return Response(
            {
                "id": result.job.id,
                "uuid": result.job.uuid,
                "cost": str(result.job.cost),
                "flags": result.job.flags,
            },
            status=status.HTTP_201_CREATED,
        )