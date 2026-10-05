"""Developer-facing routes under /api/v1/."""
from django.urls import path

from apps.jobs.api.views import JobLogView

urlpatterns = [
    path("jobs/log", JobLogView.as_view(), name="v1-jobs-log"),
]