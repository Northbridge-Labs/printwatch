"""Printers app config with DI registration on startup."""
from django.apps import AppConfig


class PrintersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.printers"

    def ready(self) -> None:
        from .containers import register_printers
        register_printers()