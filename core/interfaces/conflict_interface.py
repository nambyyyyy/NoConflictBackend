from abc import ABC, abstractmethod
from core.entities.conflict import Conflict
from uuid import UUID
from typing import TypeVar, Optional

T = TypeVar("T")


class ConflictRepository(ABC):
    
    @abstractmethod
    async def _base_get(self, filter: UUID | str) -> Conflict:
        """Базовый метод извлечения полного конфликта"""
        pass

    @abstractmethod
    async def get_by_id(self, conflict_id: UUID) -> Conflict:
        """Вернуть Conflict по conflict_id"""
        pass
    
    @abstractmethod
    async def get_by_slug(self, slug: str) -> Conflict:
        """Вернуть Conflict по slug"""
        pass

    @abstractmethod
    async def save(
        self,
        conflict: Conflict,
        update_fields: Optional[list[str]] = None,
    ) -> Conflict:
        """Создать или обновить конфликт"""
        pass
    

    
        


