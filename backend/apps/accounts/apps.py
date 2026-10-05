"""Accounts app ready hook: register DI on startup."""
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"

    def ready(self) -> None:
        from .containers import register_accounts
        register_accounts()