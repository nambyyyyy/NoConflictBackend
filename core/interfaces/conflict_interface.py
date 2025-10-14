from abc import ABC, abstractmethod
from core.entities.conflict import Conflict
from uuid import UUID
from typing import TypeVar, Optional

T = TypeVar("T")


class ConflictRepository(ABC):

    @abstractmethod
    def get_by_id(self, conflict_id: UUID) -> Conflict:
        """Вернуть Conflict по conflict_id"""
        pass
    
    @abstractmethod
    async def get_by_slug(self, slug: str) -> Conflict:
        """Вернуть Conflict по slug"""
        pass

    @abstractmethod
    def save(
        self,
        conflict: Conflict,
    ) -> Conflict:
        """Создать или обновить конфликт"""
        pass


