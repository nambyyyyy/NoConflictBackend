from infrastructure.persistence.user_repository import DjangoUserRepository
from infrastructure.persistence.token_repository import (
    DjangoTokenRepository,
    DjangoJWTRepository,
)
from infrastructure.persistence.profile_repository import DjangoProfielRepository
from infrastructure.persistence.transaction_manager import DjangoTransactionManager
from infrastructure.persistence.conflict_repository import DjangoConflictRepository, DjangoOptionChoicRepository
from infrastructure.security.django_password_hasher import DjangoPasswordHasher
from infrastructure.security.django_password_validator import DjangoPasswordValidator
from infrastructure.security.django_link_decoder import DjangoLinkDecoder
from application.services.auth_service import AuthService
from application.services.profile_service import ProfileService
from application.services.conflict_service import ConflictService
from no_conflict_project.settings import SECRET_KEY, MEDIA_URL
from infrastructure.processors.avatar.avatar_processor import DjangoAvatarProcessor
from infrastructure.processors.avatar.avatar_validator import AvatarValidator
from infrastructure.processors.avatar.filename_generator import FilenameGenerator
from infrastructure.processors.avatar.image_processor import ImageProcessor
from infrastructure.processors.avatar.image_saver import ImageSaver
from infrastructure.storage.local_storage import LocalStorage



def get_auth_service() -> AuthService:
    """Фабрика для создания AuthService"""
    return AuthService(
        user_repository=DjangoUserRepository(),
        token_repository=DjangoTokenRepository(),
        jwt_repository=DjangoJWTRepository(secret_key=SECRET_KEY, algorithm="HS256"),
        password_hasher=DjangoPasswordHasher(),
        password_validator=DjangoPasswordValidator(),
        transaction_manager=DjangoTransactionManager(),
        link_decoder=DjangoLinkDecoder(),
    )


def get_profile_service() -> ProfileService:
    """Фабрика для создания ProfileService"""
    avatar_processor = DjangoAvatarProcessor(
        validator=AvatarValidator(),
        generator=FilenameGenerator(),
        processor=ImageProcessor(),
        saver=ImageSaver(storage=LocalStorage()),
        upload_dir="avatars",
    )

    return ProfileService(
        profile_repository=DjangoProfielRepository(),
        avatar_processor=avatar_processor,
        media_base_url=MEDIA_URL,
    )

def get_conflict_service() -> ConflictService:
    """Фабрика для создания ConflictService"""
    return ConflictService(
        conflict_repository=DjangoConflictRepository(),
        option_choice_repository=DjangoOptionChoicRepository()
        
    )