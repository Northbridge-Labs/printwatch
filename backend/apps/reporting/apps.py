from django.apps import AppConfig


class ReportingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.reporting"

    def ready(self) -> None:
        from .containers import register_reporting
        register_reporting()