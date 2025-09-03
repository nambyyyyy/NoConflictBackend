from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from core.entities.profile import Profile


class ProfileRepository(ABC):
    
    @abstractmethod
    def get_by_id(self, profile_id: UUID) -> Optional[Profile]:
        """Найти профиль по ID"""
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: UUID) -> Optional[Profile]:
        """Найти профиль по ID пользователя (основной метод!)"""
        pass

    @abstractmethod
    def update(self, profile: Profile) -> Optional[Profile]:
        """Обновить профиль"""
        pass

