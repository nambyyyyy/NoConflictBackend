from abc import ABC, abstractmethod
from core.entities.conflict import Conflict
from uuid import UUID
from typing import TypeVar, List
from uuid import UUID

T = TypeVar('T')


class ConflictRepository(ABC):
    
    @abstractmethod
    def get_by_id(self, conflict_id: int) -> Conflict:
        """Вернуть Conflict по conflict_id"""
        pass
    
    @abstractmethod
    def save(self, conflict: Conflict) -> Conflict:
        """Создать или обновить конфликт"""
        pass


class OptionChoicRepository(ABC):
    
    @abstractmethod
    def get_many(self, option_ids: List[UUID]) -> List[T]:
        """Вернуть список объектов опций"""
        pass
    