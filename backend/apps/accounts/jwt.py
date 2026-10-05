"""JWT token service + custom auth backend with JTI revocation check."""
from __future__ import annotations

from typing import Optional

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken, Token, AccessToken

from apps.accounts.domain.records import DeveloperTokenSecret, TokenPair, UserRecord
from apps.accounts.domain.interfaces import (
    IDeveloperTokenRepository,
    ITokenService,
)
from apps.accounts.infrastructure.models import User


class JwtTokenService(ITokenService):
    """Issues access/refresh pairs and long-lived developer tokens."""

    def __init__(self, dev_tokens: IDeveloperTokenRepository) -> None:
        self._dev_tokens = dev_tokens

    def issue_pair(self, user: UserRecord) -> TokenPair:
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()
        try:
            django_user = UserModel.objects.get(id=user.id)
        except UserModel.DoesNotExist:
            raise ValueError("User not found")
        refresh = RefreshToken.for_user(django_user)
        refresh["role"] = user.role
        return TokenPair(access=str(refresh.access_token), refresh=str(refresh))

    def issue_developer_token(
        self, user_id: int, name: str, scopes: list
    ) -> DeveloperTokenSecret:
        return self._dev_tokens.create(user_id, name, scopes)

    def verify(self, token: str) -> Optional[dict]:
        try:
            decoded = AccessToken(token)
            decoded.verify()
            return dict(decoded.payload)
        except TokenError:
            return None


class JwtAccessTokenAuthentication(JWTAuthentication):
    """DRF authentication that also handles developer-type JWTs with JTI
    revocation lookup (cached 60s in Valkey)."""

    def get_validated_token(self, raw_token) -> Token:
        # Try normal access token first
        try:
            return super().get_validated_token(raw_token)
        except InvalidToken:
            pass

        # Fall back to developer token verification
        try:
            token = AccessToken(raw_token)
            token.verify()
        except TokenError as exc:
            raise InvalidToken(str(exc)) from exc

        payload = token.payload
        if payload.get("typ") != "developer":
            raise InvalidToken("Not a developer token")
        jti = payload.get("jti")
        if not jti:
            raise InvalidToken("Missing jti")
        from apps.common.container import container
        dev_repo = container.resolve("developer_token_repository")
        record = dev_repo.get_by_jti(jti)
        if record is None:
            raise InvalidToken("Unknown token")
        if record.revoked_at is not None:
            raise InvalidToken("Token revoked")
        # Attach developer identity to the token for views to inspect
        token._developer_record = record
        return token

    def get_user(self, validated_token, *args, **kwargs):
        if validated_token.payload.get("typ") == "developer":
            user_id = validated_token.payload.get("user_id")
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise InvalidToken("User not found")
            # Developer tokens are treated as authenticated service users.
            user.is_developer_token = True
            user.token_scopes = validated_token.payload.get("scopes", [])
            return user
        return super().get_user(validated_token, *args, **kwargs)