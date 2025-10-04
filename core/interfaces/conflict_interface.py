from abc import ABC, abstractmethod
from core.entities.conflict import Conflict
from uuid import UUID
from typing import TypeVar

T = TypeVar('T')


class ConflictRepository(ABC):
    
    @abstractmethod
    def get_by_id(self, conflict_id: UUID) -> Conflict:
        """Вернуть Conflict по conflict_id"""
        pass
    
    @abstractmethod
    def save(self, conflict: Conflict) -> Conflict:
        """Создать или обновить конфликт"""
        pass

