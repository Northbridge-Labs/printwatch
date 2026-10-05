"""Accounts URL routes."""
from django.urls import path

from .views import (
    DeveloperTokenListView,
    DeveloperTokenRevokeView,
    EmailTokenObtainPairView,
    EmailTokenRefreshView,
    MeView,
)

urlpatterns = [
    path("auth/login", EmailTokenObtainPairView.as_view(), name="login"),
    path("auth/refresh", EmailTokenRefreshView.as_view(), name="refresh"),
    path("auth/me", MeView.as_view(), name="me"),
    path("developer-tokens", DeveloperTokenListView.as_view(), name="developer-tokens"),
    path("developer-tokens/<int:token_id>/revoke",
         DeveloperTokenRevokeView.as_view(), name="developer-token-revoke"),
]