"""Internal ingest routes (under /api/ingest/)."""
from django.urls import path

from .views_internal import InternalIngestView

urlpatterns = [
    path("jobs", InternalIngestView.as_view(), name="internal-ingest-jobs"),
]