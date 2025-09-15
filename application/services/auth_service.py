from core.interfaces.user_repository import UserRepository
from core.interfaces.token_repository import TokenRepository, JWTTRepository
from core.interfaces.password_repository import PasswordHasher, PasswordValidator
from core.interfaces.transaction_repository import TransactionManager
from core.interfaces.link_repository import LinkDecoder
from application.dtos.user_dto import UserDTO
from core.entities.user import User
from uuid import uuid4
from datetime import datetime
from typing import Callable, Optional
from uuid import UUID



class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        token_repository: TokenRepository,
        jwt_repository: JWTTRepository,
        password_hasher: PasswordHasher,
        password_validator: PasswordValidator,
        transaction_manager: TransactionManager,
        link_decoder: LinkDecoder,
    ):
        self.user_repo = user_repository
        self.token_repo = token_repository
        self.jwt_repository = jwt_repository
        self.password_hasher = password_hasher
        self.password_validator = password_validator
        self.transaction_manager = transaction_manager
        self.link_decoder = link_decoder

    def register_user(
        self,
        email: str,
        username: str,
        password: str,
        send_email_func: Callable,
        base_url: str,
    ) -> UserDTO:

        self._validate_registration(email, username, password)
        user_entity: User = self._create_user_entity(email, username, password)
        saved_entity: User = self.user_repo.save(user_entity)
        token: str = self.token_repo.make_token(user_entity)

        self.transaction_manager.on_commit(
            lambda: send_email_func(str(user_entity.id), token, base_url=base_url)
        )
        return self._to_dto(user_entity=saved_entity)

    def verify_email(self, uidb64: str, token: str) -> UserDTO:
        try:
            user_id_str: str = self.link_decoder.decode(uidb64)
            user_id = UUID(user_id_str)
        except (TypeError, ValueError, OverflowError, UnicodeDecodeError):
            raise ValueError("Invalid verification link")

        user_entity: Optional[User] = self.user_repo.get_by_id(user_id=user_id)
        if user_entity is None:
            raise ValueError("Пользователь не найден")

        self._validate_verify(user_entity)

        if not self.token_repo.check_token(user_entity, token):
            raise ValueError("Закончился срок действия токена")

        user_entity.email_confirmed = True
        updated_entity: Optional[User] = self.user_repo.update(user_entity)
        if updated_entity is None:
            raise ValueError("Пользователь не найден")

        return self._to_dto(user_entity=updated_entity)

    def login(self, login: str, password: str) -> dict[str, str]:
        user_entity = self.user_repo.get_by_email(login)
        if not user_entity:
            user_entity = self.user_repo.get_by_username(login)

        self._validate_login(user_entity, password)

        access_token = self.jwt_repository.create_access_token(user_entity)
        refresh_token = self.jwt_repository.create_refresh_token(user_entity)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
        }

    def _validate_registration(self, email: str, username: str, password: str) -> None:
        if self.user_repo.get_by_email(email):
            raise ValueError("User with this email already exists")

        if self.user_repo.get_by_username(username):
            raise ValueError("User with this username already exists")

        self.password_validator.validate(password)

    def _validate_verify(self, user_entity: User | None) -> None:
        if not user_entity:
            raise ValueError("The user with this uuid was not found")
        if user_entity.email_confirmed:
            raise ValueError("Email уже подтвержден")

        self._chek_delete_or_block(user_entity)

    def _validate_login(self, user_entity: Optional[User], password: str):
        if not user_entity or not self.password_hasher.verify(
            password, user_entity.password_hash
        ):
            raise ValueError("Неверный логин или пароль")

        if not user_entity.email_confirmed:
            raise ValueError("Подтвердите email для входа")

        self._chek_delete_or_block(user_entity)

    def _chek_delete_or_block(self, user_entity: User) -> None:
        if not user_entity.is_active:
            raise ValueError("Аккаунт заблокирован")
        if user_entity.is_deleted:
            raise ValueError("Пользователь удален")

    def _create_user_entity(self, email: str, username: str, password: str) -> User:
        return User(
            id=uuid4(),
            email=email,
            username=username,
            password_hash=self.password_hasher.hash(password),
            created_at=datetime.now(),
        )

    def _to_dto(self, user_entity: User) -> UserDTO:
        return UserDTO(
            id=user_entity.id,
            email=user_entity.email,
            username=user_entity.username,
            email_confirmed=user_entity.email_confirmed,
        )
        #
