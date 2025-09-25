from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    
    @abstractmethod
    def hash(self, plain_password: str) -> str:
        """Создаёт хэш пароля"""
        pass
    
    @abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Проверяет, соответствует ли пароль хэшу"""
        pass


class PasswordValidator(ABC):
    
    @abstractmethod
    def validate(self, plain_password: str) -> None:
        """
        Проверяет пароль на соответствие правилам безопасности.
        Должен кидать ValueError (или кастомное DomainException),
        если пароль не проходит валидацию.
        """
        pass