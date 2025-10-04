from core.interfaces.conflict_interface import (
    ConflictRepository,
)
from core.interfaces.user_interface import UserRepository
from application.dtos.conflict_dto import (
    ConflictDetailDTO,
)
from core.entities.conflict import Conflict, ConflictError
from core.entities.conflict_item import ConflictItem
from core.entities.conflict_event import ConflictEvent
from typing import Any, Optional, Callable
from uuid import uuid4, UUID


class ConflictService:
    def __init__(
        self,
        conflict_repository: ConflictRepository,
        user_repository: UserRepository,
    ):
        self.conflict_repo = conflict_repository
        self.user_repository = user_repository

    def create_conflict(
        self,
        creator_id: UUID,
        validated_data: dict[str, Any],
        transaction_atomic: Callable,
    ) -> ConflictDetailDTO:
        creator_id, partner_id, title, items, events = self._validate_conflict(
            creator_id,
            validated_data.get("partner_id"),
            validated_data.get("title"),
            validated_data.get("items"),
            validated_data.get("events"),
        )

        conflict_entity: Conflict = Conflict(
            creator_id=creator_id,
            partner_id=partner_id,
            title=title,
            items=items,
            events=events,
        )
        with transaction_atomic():
            saved_conflict: Conflict = self.conflict_repo.save(conflict_entity)

        return self._to_dto_detail(saved_conflict)

    def _validate_conflict(
        self,
        creator_id: UUID,
        partner_id: Optional[UUID] = None,
        title: Optional[str] = None,
        items: Optional[list] = None,
        events: Optional[list] = None,
    ) -> tuple[UUID, Optional[UUID], str, list[dict], list[dict]]:
        if partner_id is not None:
            if creator_id == partner_id:
                raise ConflictError("Нельзя назначить партнером самого себя")

        if title is None:
            title = self._generate_title()

        self._validate_items(items)

        if not events:
            raise ConflictError("Нельзя создать конфликт без единого события")

        return creator_id, partner_id, title, items, events  # type: ignore

    def _validate_items(self, items: Optional[list]) -> None:
        if not items:
            raise ConflictError("Для создания конфликта нужен минимум один пункт")

        for item in items:
            if not item["title"]:
                raise ConflictError("У item нет title")
            if not item["creator_choice_value"]:
                raise ConflictError("У item нет creator_choice_value")

    def _generate_title(self) -> str:
        short_id = str(uuid4()).replace("-", "")[:8]
        return f"Conflict - {short_id.upper()}"

    def _to_dto_detail(self, conflict: Conflict) -> ConflictDetailDTO:
        return ConflictDetailDTO(
            id=conflict.id,
            creator_id=conflict.creator_id,
            partner_id=conflict.partner_id,
            title=conflict.title,
            status=conflict.status,
            slug=conflict.slug,
            progress=conflict.progress,
            resolved_at=conflict.resolved_at,
            truce_status=conflict.truce_status,
            truce_initiator_id=conflict.truce_initiator_id,
            items=self._to_item_dict(conflict.items),
            events=self._to_event_dict(conflict.items)
        )

    def _to_item_dict(self, items: list[ConflictItem]) -> list[dict]:
        items_data = []
        for item in items:
            items_data.append(
                {
                    "title": str(item.title),
                    "creator_choice_value": (
                        str(item.creator_choice_value)
                        if item.creator_choice_value
                        else ""
                    ),
                    "partner_choice_value": (
                        str(item.partner_choice_value)
                        if item.partner_choice_value
                        else ""
                    ),
                    "agreed_choice_value": (
                        str(item.agreed_choice_value)
                        if item.agreed_choice_value
                        else ""
                    ),
                    "is_agreed": bool(item.is_agreed),
                }
            )
        return items_data

    def _to_event_dict(self, events: list[ConflictEvent]) -> list[dict]:
        event_data = []
        for event in events:
            event_data.append(
                {
                    "id": event.id,
                    "created_at": event.created_at,
                    "initiator": event.initiator,
                    "event_type": event.event_type,
                    "item_id": event.item_id,
                    "old_value": event.old_value,
                    "new_value": event.new_value,
                }
            )
        return event_data
