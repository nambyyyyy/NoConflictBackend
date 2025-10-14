from abc import ABC, abstractmethod
from core.entities.conflict_item import ConflictItem
from typing import Optional
from uuid import UUID

class ItemRepository(ABC):

    @abstractmethod
    async def save(
        self,
        item: ConflictItem,
        update_fields: Optional[list[str]] = None
    ) -> ConflictItem:
        """Создать или обновить item конфликта"""
        pass

    @abstractmethod
    async def get_by_id_and_conflict_id(
        self, item_id: UUID, conflict_id: UUID
    ) -> Optional[ConflictItem]:
        """Найти конфликт по item_id и conflict_id"""
        pass
