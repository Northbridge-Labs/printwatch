"""Accounts domain records (framework-agnostic)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class UserRecord:
    id: int
    email: str
    role: str
    is_active: bool
    department_id: Optional[int] = None
    username: Optional[str] = None


@dataclass(frozen=True)
class DeveloperTokenRecord:
    id: int
    user_id: int
    name: str
    jti: UUID
    scopes: list = field(default_factory=list)
    revoked_at: Optional[str] = None


@dataclass(frozen=True)
class TokenPair:
    access: str
    refresh: str


@dataclass(frozen=True)
class DeveloperTokenSecret:
    token_id: int
    jti: UUID
    jwt: str  # signed JWT, returned only once at mint time