from abc import ABC, abstractmethod
from core.entities.conflict_item import ConflictItem
from uuid import UUID

class ItemRepository(ABC):

    @abstractmethod
    def save(
        self,
        item: ConflictItem,
    ) -> ConflictItem:
        """Создать или обновить item конфликта"""
        pass
