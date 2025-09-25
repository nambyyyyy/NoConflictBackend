from abc import ABC, abstractmethod
from core.entities.conflict import Conflict

class ConflictRepository(ABC):
    
    @abstractmethod
    def get_by_id(self, conflict_id: int) -> Conflict:
        """Вернуть Conflict по conflict_id"""
        pass
    
    @abstractmethod
    def save(self, conflict: Conflict) -> Conflict:
        """Создать или обновить конфликт"""
        pass


    