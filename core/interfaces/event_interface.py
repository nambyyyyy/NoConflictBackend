from abc import ABC, abstractmethod
from core.entities.conflict_event import ConflictEvent


class EventRepository(ABC):

    @abstractmethod
    async def save(
        self,
        event: ConflictEvent
    ) -> ConflictEvent:
        """Создать или обновить event конфликта"""
        pass