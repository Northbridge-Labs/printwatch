"""Accounts serializers."""
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.accounts.infrastructure.models import DeveloperToken

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "role", "phone", "department", "is_active"]
        read_only_fields = ["id"]


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Login using email instead of username."""

    username_field = User.EMAIL_FIELD

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["email"] = user.email
        return token


class DeveloperTokenSerializer(serializers.ModelSerializer):
    """Serializer for listing developer tokens (without the JWT secret)."""

    class Meta:
        model = DeveloperToken
        fields = ["id", "name", "jti", "scopes", "created_at", "revoked_at"]
        read_only_fields = ["id", "jti", "created_at", "revoked_at"]


class MintDeveloperTokenSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=128)
    scopes = serializers.ListField(
        child=serializers.CharField(max_length=64),
        required=False,
        default=list,
    )


class MintDeveloperTokenResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    jti = serializers.UUIDField()
    token = serializers.CharField(help_text="Signed JWT. Returned only once.")