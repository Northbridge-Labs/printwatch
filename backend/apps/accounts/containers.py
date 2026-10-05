"""DI wiring for accounts app."""
from apps.accounts.infrastructure.repositories import (
    DjangoDeveloperTokenRepository,
    DjangoUserRepository,
)
from apps.accounts.jwt import JwtTokenService
from apps.accounts.services.auth import AuthService, DeveloperTokenService
from apps.common.container import container


def register_accounts() -> None:
    user_repo = DjangoUserRepository()
    dev_repo = DjangoDeveloperTokenRepository()
    token_service = JwtTokenService(dev_repo)
    container.register("user_repository", lambda: user_repo)
    container.register("developer_token_repository", lambda: dev_repo)
    container.register("token_service", lambda: token_service)
    container.register(
        "auth_service",
        lambda: AuthService(user_repo, token_service),
    )
    container.register(
        "developer_token_service",
        lambda: DeveloperTokenService(dev_repo),
    )