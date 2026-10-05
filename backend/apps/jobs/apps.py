"""Jobs app config with DI registration on startup."""
from django.apps import AppConfig


class JobsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.jobs"

    def ready(self) -> None:
        from .containers import register_jobs
        register_jobs()