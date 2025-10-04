from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from core.entities.user import User


class UserRepository(ABC):

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """Найти пользователя по email (для проверки существования)"""
        pass
    
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """Найти пользователя по username (понадобится для подтверждения username)"""
        pass
    
    @abstractmethod
    def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Найти пользователя по ID (понадобится для подтверждения email)"""
        pass
    
    @abstractmethod
    def get_many_id(self, user_ids: list[UUID]) -> Optional[list[User]]:
        """Найти пользователя по ID (понадобится для подтверждения email)"""
        pass

    @abstractmethod
    def save(self, user: User) -> User:
        """Сохранить пользователя (создать или обновить)"""
        pass

    @abstractmethod
    def update(self, user: User) -> User:
        """Обновить пользователя (для подтверждения email, смены пароля)"""
        pass
    
    @abstractmethod  
    def delete(self, user_id: UUID) -> None:
        """Удалить пользователя"""
        pass
