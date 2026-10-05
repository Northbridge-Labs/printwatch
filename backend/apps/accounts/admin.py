"""Admin registration for accounts."""
from django.contrib import admin

from apps.accounts.infrastructure.models import DeveloperToken, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "role", "is_active", "department")
    list_filter = ("role", "is_active")
    search_fields = ("email",)
    ordering = ("email",)


@admin.register(DeveloperToken)
class DeveloperTokenAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "jti", "created_at", "revoked_at")
    list_filter = ("revoked_at",)
    search_fields = ("name", "user__email")
    ordering = ("-created_at",)