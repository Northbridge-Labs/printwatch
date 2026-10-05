"""Accounts services: business logic depending only on domain interfaces."""
from __future__ import annotations

from typing import Optional

from apps.accounts.domain.records import (
    DeveloperTokenRecord,
    DeveloperTokenSecret,
    TokenPair,
)
from apps.accounts.domain.interfaces import (
    IDeveloperTokenRepository,
    IUserRepository,
    ITokenService,
)


class AuthService:
    """Orchestrates login + token issuance using injected repositories."""

    def __init__(
        self,
        users: IUserRepository,
        tokens: ITokenService,
    ) -> None:
        self._users = users
        self._tokens = tokens

    def login(self, email: str, password: str) -> Optional[TokenPair]:
        user = self._users.get_by_email(email)
        if user is None or not user.is_active:
            return None
        if not self._users.verify_password(user.id, password):
            return None
        return self._tokens.issue_pair(user)


class DeveloperTokenService:
    """Manage long-lived developer tokens (mint, list, revoke)."""

    def __init__(self, dev_tokens: IDeveloperTokenRepository) -> None:
        self._dev_tokens = dev_tokens

    def mint(
        self, user_id: int, name: str, scopes: list
    ) -> DeveloperTokenSecret:
        if not name:
            raise ValueError("Token name is required")
        return self._dev_tokens.create(user_id, name, scopes)

    def list(self, user_id: int) -> list[DeveloperTokenRecord]:
        return self._dev_tokens.list_for_user(user_id)

    def revoke(self, token_id: int) -> None:
        self._dev_tokens.revoke(token_id)