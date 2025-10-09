from abc import ABC, abstractmethod
from core.entities.conflict_event import ConflictEvent
from uuid import UUID
from typing import Optional


class EventRepository(ABC):

    @abstractmethod
    def save(
        self,
        conflict_id: UUID,
        event_type: str,
        user_id: Optional[UUID] = None,
        item_id: Optional[UUID] = None,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None
    ) -> ConflictEvent:
        """Создать или обновить event конфликта"""
        pass