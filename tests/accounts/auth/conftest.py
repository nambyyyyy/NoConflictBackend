import pytest
from unittest.mock import Mock
from application.services.auth_service import AuthService
from backend.core.interfaces.user_interface import UserRepository
from backend.core.interfaces.token_interface import TokenRepository, JWTTRepository
from backend.core.interfaces.password_interface import PasswordHasher, PasswordValidator
from backend.core.interfaces.transaction_interface import TransactionManager
from backend.core.interfaces.link_interface import LinkDecoder
from uuid import UUID
from typing import Optional
from datetime import datetime



@pytest.fixture
def auth_service():
    mock_user_repo = Mock(spec=UserRepository)
    mock_token_repo = Mock(spec=TokenRepository)
    mock_jwt_repo = Mock(spec=JWTTRepository)
    mock_password_hasher = Mock(spec=PasswordHasher)
    mock_password_validator = Mock(spec=PasswordValidator)
    mock_transaction_manager = Mock(spec=TransactionManager)
    mock_link_decoder = Mock(spec=LinkDecoder)
    
    mock_transaction_manager.on_commit.side_effect = lambda func: func()
    
    return AuthService(
        mock_user_repo,
        mock_token_repo,
        mock_jwt_repo,
        mock_password_hasher,
        mock_password_validator,
        mock_transaction_manager,
        mock_link_decoder,
    )


@pytest.fixture
def mock_token_repo(auth_service):
    return auth_service.token_repo


@pytest.fixture
def mock_user_repo(auth_service):
    return auth_service.user_repo


@pytest.fixture
def fake_user_class():
    """Фикстура, возвращающая фейковый класс User без зависимостей от Django."""

    class FakeUser:
        def __init__(
            self,
            id: UUID,
            email: str,
            username: str,
            password_hash: str,
            email_confirmed: bool = False,
            is_active: bool = True,
            is_deleted: bool = False,
            created_at: Optional[datetime] = None,
            updated_at: Optional[datetime] = None,
        ):
            self.id = id
            self.email = email
            self.username = username
            self.password_hash = password_hash
            self.email_confirmed = email_confirmed
            self.is_active = is_active
            self.is_deleted = is_deleted
            self.created_at = created_at or datetime.now()
            self.updated_at = updated_at

        def set_password(self, raw_password: str):
            """Имитация хеширования — просто добавляем префикс "hashed_"."""
            self.password_hash = "hashed_" + raw_password

    return FakeUser
