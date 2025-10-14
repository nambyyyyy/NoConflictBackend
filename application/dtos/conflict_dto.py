from dataclasses import dataclass
from uuid import UUID
from typing import Optional, Any
from datetime import datetime
from abc import ABC, abstractmethod


class BaseConflictDTO(ABC):

    @abstractmethod
    def to_dict(self):
        """Переопределить метод конвертации из объекта в словарь"""
        pass


@dataclass
class ConflictItemDTO(BaseConflictDTO):
    id: UUID
    title: str
    creator_choice_value: Optional[str]
    partner_choice_value: Optional[str]
    agreed_choice_value: Optional[str]
    is_agreed: bool

    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "creator_choice_value": self.creator_choice_value,
            "partner_choice_value": self.partner_choice_value,
            "agreed_choice_value": self.agreed_choice_value,
            "is_agreed": self.is_agreed,
        }


@dataclass
class ConflictEventDTO(BaseConflictDTO):
    id: UUID
    event_type: str
    created_at: datetime
    initiator: Optional[dict[str, Any]]
    item_id: Optional[UUID]
    old_value: Optional[str]
    new_value: Optional[str]

    def to_dict(self):
        return {
            "id": str(self.id),
            "event_type": self.event_type,
            "created_at": self.created_at.isoformat(),
            "initiator": self.initiator,
            "item_id": str(self.item_id) if self.item_id else None,
            "old_value": self.old_value,
            "new_value": self.new_value,
        }


@dataclass
class ConflictDetailDTO(BaseConflictDTO):
    id: UUID
    creator_id: UUID
    partner_id: Optional[UUID]
    title: Optional[str]
    status: str
    slug: str
    progress: float
    created_at: datetime
    resolved_at: Optional[datetime]
    truce_status: str
    truce_initiator_id: Optional[UUID]
    items: list[dict]
    events: list[dict]

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "creator_id": str(self.creator_id),
            "partner_id": str(self.partner_id),
            "title": self.title,
            "status": self.status,
            "slug": self.slug,
            "progress": self.progress,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "truce_status": self.truce_status,
            "truce_initiator_id": (
                str(self.truce_initiator_id) if self.truce_initiator_id else None
            ),
            "items": self.items,
            "events": self.events,
        }


@dataclass
class ConflictShortDTO(BaseConflictDTO):
    id: UUID
    creator_id: UUID
    partner_id: Optional[UUID]
    title: Optional[str]
    status: str
    progress: float
    resolved_at: Optional[datetime]

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "creator_id": str(self.creator_id),
            "partner_id": str(self.partner_id),
            "title": self.title,
            "status": self.status,
            "progress": self.progress,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }