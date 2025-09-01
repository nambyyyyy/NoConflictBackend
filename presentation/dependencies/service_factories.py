# presentation/dependencies.py
from infrastructure.persistence.user_repository import DjangoUserRepository
from infrastructure.persistence.token_repository import (
    DjangoTokenRepository,
    DjangoJWTRepository,
)
from application.services import AuthService
from no_conflict_project.settings import SECRET_KEY


def get_auth_service() -> AuthService:
    """Фабрика для создания AuthService"""
    user_repo = DjangoUserRepository()
    token_repo = DjangoTokenRepository()
    jwt_repo = DjangoJWTRepository(secret_key=SECRET_KEY, algorithm="HS256")
    return AuthService(
        user_repository=user_repo, token_repository=token_repo, jwt_repository=jwt_repo
    )
