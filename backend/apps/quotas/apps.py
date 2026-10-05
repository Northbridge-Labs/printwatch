"""Quotas app config with DI registration on startup."""
from django.apps import AppConfig


class QuotasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.quotas"

    def ready(self) -> None:
        from .containers import register_quotas
        register_quotas()