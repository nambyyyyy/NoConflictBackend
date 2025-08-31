from core.repositories.user_repository import UserRepository
from application.dtos.user_dto import UserDTO
from core.entities.user import User
from uuid import uuid4
from datetime import datetime
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repo = user_repository

    def register_user(self, email: str, username: str, password: str) -> UserDTO:
        # 1. Проверяем, не существует ли email
        if self.user_repo.get_by_email(email):
            raise ValueError("User with this email already exists")
        
        # 2. Проверяем, не существует ли пользователь
        if self.user_repo.get_by_username(username):
            raise ValueError("User with this username already exists")
        
        try:
            validate_password(password)  # Django password validation
        except DjangoValidationError as e:
            raise ValueError(f"Слабый пароль: {', '.join(e.messages)}")

        # 3. Хешируем пароль
        password_hash = make_password(password)
        
        # 4. Создаем сущность User
        user_entity = User(
            id=uuid4(),
            email=email,
            username=username,
            password_hash=password_hash,
            created_at=datetime.now(),
        )

        # 5. Сохраняем Entity через репозиторий
        saved_entity = self.user_repo.save(user_entity)

        # 5. Возвращаем DTO (только данные для наружного мира)
        return UserDTO(
            id=saved_entity.id,
            email=saved_entity.email,
            username=saved_entity.username,
            email_confirmed=saved_entity.email_confirmed,
        )
