"""Reporting views: read-only aggregate endpoints."""
from datetime import datetime

from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.common.container import container


def _parse_range(request):
    end = request.query_params.get("end")
    start = request.query_params.get("start")
    end_dt = datetime.strptime(end, "%Y-%m-%d").date() if end else None
    start_dt = datetime.strptime(start, "%Y-%m-%d").date() if start else None
    return start_dt, end_dt


@extend_schema(tags=["Reporting"])
class SummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        start, end = _parse_range(request)
        svc = container.resolve("reporting_service")
        return Response(svc.summary(start, end))


@extend_schema(tags=["Reporting"])
class PagesByUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        start, end = _parse_range(request)
        job_type = request.query_params.get("type")
        if not (start and end):
            return Response({"detail": "start and end required"}, status=400)
        svc = container.resolve("reporting_service")
        return Response(svc.pages_by_user(start, end, job_type))


@extend_schema(tags=["Reporting"])
class PagesByPrinterView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        start, end = _parse_range(request)
        job_type = request.query_params.get("type")
        if not (start and end):
            return Response({"detail": "start and end required"}, status=400)
        svc = container.resolve("reporting_service")
        return Response(svc.pages_by_printer(start, end, job_type))


@extend_schema(tags=["Reporting"])
class JobsByTypeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        start, end = _parse_range(request)
        if not (start and end):
            return Response({"detail": "start and end required"}, status=400)
        svc = container.resolve("reporting_service")
        return Response(svc.jobs_by_type(start, end))


@extend_schema(tags=["Reporting"])
class CostTrendView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        start, end = _parse_range(request)
        job_type = request.query_params.get("type")
        if not (start and end):
            return Response({"detail": "start and end required"}, status=400)
        svc = container.resolve("reporting_service")
        return Response(svc.cost_trend(start, end, job_type))