"""Internal ingest endpoint used by the zmq-consumer.

Tagged ``internal`` so the preprocessing hook hides it from the public
Swagger UI. Uses a service token (header ``X-Ingest-Token``), not JWT.
"""
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.container import container

from .serializers import JobLogRequestSerializer


class InternalIngestView(APIView):
    """Receive a job payload from the zmq-consumer daemon."""

    permission_classes = [permissions.AllowAny]  # service-token checked below

    @extend_schema(
        tags=["internal"],
        exclude=True,
        request=JobLogRequestSerializer,
        responses={201: dict},
    )
    def post(self, request):
        token = request.headers.get("X-Ingest-Token", "")
        from django.conf import settings
        if token != settings.INGEST_SERVICE_TOKEN:
            return Response({"detail": "Invalid ingest token"}, status=401)

        serializer = JobLogRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        from apps.jobs.services.processors import IngestionProcessorFactory

        source = request.data.get("source", "cups")
        processor = IngestionProcessorFactory.get(source)
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
            "raw": request.data.get("raw", {}),
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