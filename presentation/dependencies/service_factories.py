from infrastructure.persistence.user_repository import DjangoUserRepository
from infrastructure.persistence.token_repository import (
    DjangoTokenRepository,
    DjangoJWTRepository,
)
from infrastructure.persistence.profile_repository import DjangoProfielRepository
from application.services.auth_service import AuthService
from application.services.profile_service import ProfileService
from no_conflict_project.settings import SECRET_KEY, MEDIA_URL
from infrastructure.processors.avatar_processor import AvatarProcessor
from infrastructure.storage.local_storage import LocalStorage


def get_auth_service() -> AuthService:
    """Фабрика для создания AuthService"""
    return AuthService(
        user_repository=DjangoUserRepository(),
        token_repository=DjangoTokenRepository(),
        jwt_repository=DjangoJWTRepository(secret_key=SECRET_KEY, algorithm="HS256"),
    )


def get_profile_service() -> ProfileService:
    return ProfileService(
        profile_repository=DjangoProfielRepository(),
        avatar_processor=AvatarProcessor(storage=LocalStorage()),
        media_base_url=MEDIA_URL
    )
