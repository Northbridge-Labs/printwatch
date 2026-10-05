"""Accounts permissions."""
from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    message = "Administrator role required."

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and getattr(request.user, "role", None) == "admin"
        )


class IsOperatorOrAdmin(BasePermission):
    message = "Operator or administrator role required."

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and getattr(request.user, "role", None) in ("admin", "operator")
        )


class HasScope(BasePermission):
    """Check that a developer token has a given scope.

    Usage: ``permission_classes = [HasScope]`` and set ``required_scopes``
    on the view.
    """

    def has_permission(self, request, view):
        scopes = getattr(request.user, "token_scopes", None) or []
        if not scopes:
            # Not a developer token — fall through to other permission classes.
            return True
        required = set(getattr(view, "required_scopes", []))
        return required.issubset(set(scopes))