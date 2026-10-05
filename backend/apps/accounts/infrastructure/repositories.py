"""Accounts repositories: ORM access implementing domain interfaces."""
from __future__ import annotations

from datetime import timedelta
from typing import Optional
from uuid import uuid4

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from apps.accounts.domain.records import (
    DeveloperTokenRecord,
    DeveloperTokenSecret,
    UserRecord,
)
from apps.accounts.infrastructure.models import DeveloperToken, User

_JTI_CACHE_KEY = "devtoken:jti:{jti}"


def _to_user_record(u: User) -> UserRecord:
    return UserRecord(
        id=u.id,
        email=u.email,
        role=u.role,
        is_active=u.is_active,
        department_id=u.department_id,
        username=u.username,
    )


class DjangoUserRepository:
    def get_by_email(self, email: str) -> Optional[UserRecord]:
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return None
        return _to_user_record(user)

    def get_by_id(self, user_id: int) -> Optional[UserRecord]:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
        return _to_user_record(user)

    def verify_password(self, user_id: int, password: str) -> bool:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return False
        return user.check_password(password)


class DjangoDeveloperTokenRepository:
    def create(self, user_id: int, name: str, scopes: list) -> DeveloperTokenSecret:
        jti = uuid4()
        from rest_framework_simplejwt.tokens import AccessToken

        token = AccessToken()
        token["jti"] = str(jti)
        token["typ"] = "developer"
        token["user_id"] = user_id
        token["scopes"] = list(scopes)
        token.set_exp(lifetime=timedelta(days=settings.JWT_DEV_TOKEN_YEARS * 365))

        DeveloperToken.objects.create(
            user_id=user_id, name=name, jti=jti, scopes=list(scopes),
        )
        return DeveloperTokenSecret(
            token_id=DeveloperToken.objects.get(jti=jti).id,
            jti=jti,
            jwt=str(token),
        )

    def list_for_user(self, user_id: int) -> list[DeveloperTokenRecord]:
        qs = DeveloperToken.objects.filter(user_id=user_id).order_by("-created_at")
        return [
            DeveloperTokenRecord(
                id=t.id, user_id=t.user_id, name=t.name, jti=t.jti,
                scopes=t.scopes, revoked_at=(
                    t.revoked_at.isoformat() if t.revoked_at else None
                ),
            )
            for t in qs
        ]

    def revoke(self, token_id: int) -> None:
        DeveloperToken.objects.filter(id=token_id).update(
            revoked_at=timezone.now()
        )
        # Invalidate JTI cache so revocation takes effect immediately.
        for t in DeveloperToken.objects.filter(id=token_id):
            cache.delete(_JTI_CACHE_KEY.format(jti=t.jti))

    def get_by_jti(self, jti: str) -> Optional[DeveloperTokenRecord]:
        cache_key = _JTI_CACHE_KEY.format(jti=jti)
        record: Optional[DeveloperTokenRecord] = cache.get(cache_key)
        if record is not None:
            return record
        try:
            t = DeveloperToken.objects.get(jti=jti)
        except DeveloperToken.DoesNotExist:
            return None
        record = DeveloperTokenRecord(
            id=t.id, user_id=t.user_id, name=t.name, jti=t.jti,
            scopes=t.scopes, revoked_at=(
                t.revoked_at.isoformat() if t.revoked_at else None
            ),
        )
        if record.revoked_at is None:
            cache.set(cache_key, record, 60)
        return record