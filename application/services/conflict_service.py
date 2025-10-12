from core.interfaces.conflict_interface import (
    ConflictRepository,
)
from core.interfaces.item_interface import ItemRepository
from core.interfaces.event_interface import EventRepository
from application.dtos.conflict_dto import (
    ConflictDetailDTO,
    ConflictItemDTO,
    ConflictEventDTO,
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
        item_repository: ItemRepository,
        event_repository: EventRepository,
    ):
        self.conflict_repo = conflict_repository
        self.item_repo = item_repository
        self.event_repo = event_repository

    def get_conflict(self, user_id: UUID, slug: str) -> ConflictDetailDTO:
        conflict_entity: Conflict = self.conflict_repo.get_by_slug(slug)
        self._validate_access_conflict(conflict_entity, user_id)
        return self._to_conflict_dto_detail(conflict_entity)

    def create_conflict(
        self,
        creator_id: UUID,
        validated_data: dict[str, Any],
        transaction_atomic: Callable,
    ) -> ConflictDetailDTO:

        self._validate_conflict_registration(
            creator_id,
            validated_data.get("partner_id"),
            validated_data.get("title"),
            validated_data.get("items"),
        )

        conflict_entity: Conflict = Conflict(
            creator_id=creator_id,
            partner_id=validated_data.get("partner_id"),
            title=validated_data.get("title"), # type: ignore
        )
        items_entity: list[ConflictItem] = [
            ConflictItem(
                id=item.get("id"),  # type: ignore
                conflict_id=conflict_entity.id,
                title=item.get("title"),  # type: ignore
                creator_choice_value=item.get("creator_choice_value"),
            )
            for item in validated_data.get("items") # type: ignore
        ]

        with transaction_atomic():
            saved_conflict: Conflict = self.conflict_repo.save(
                conflict_entity, creator_id
            )
            saved_items: list[ConflictItem] = [
                self.item_repo.save(item) for item in items_entity
            ]

            saved_events: list[ConflictEvent] = []
            event_create = self.event_repo.save(
                conflict_id=saved_conflict.id,
                event_type="conflict_create",
                user_id=saved_conflict.creator_id,
            )
            saved_events.append(event_create)

            for item in saved_items:
                saved_events.append(
                    self.event_repo.save(
                        conflict_id=saved_conflict.id,
                        event_type="item_add",
                        user_id=saved_conflict.creator_id,
                        item_id=item.id,
                        new_value=item.creator_choice_value,
                    )
                )

            saved_conflict.items = saved_items
            saved_conflict.events = saved_events

        return self._to_conflict_dto_detail(saved_conflict)

    def _validate_conflict_registration(
        self,
        creator_id: UUID,
        partner_id: Optional[UUID],
        title: Optional[str],
        items: Optional[list],
    ) -> None:
        if partner_id is not None and (creator_id == partner_id):
            raise ConflictError("Нельзя назначить партнером самого себя")

        if title is None:
            raise ConflictError("Название конфликта обязательно")

        self._validate_items_registration(items)

    def _validate_items_registration(self, items: Optional[list]) -> None:
        if not items:
            raise ConflictError("Для создания конфликта нужен минимум один пункт")

        for item in items:
            if not item["title"]:
                raise ConflictError("У item нет title")
            if not item["creator_choice_value"]:
                raise ConflictError("У item нет creator_choice_value")

    def _validate_access_conflict(
        self, conflict: Optional[Conflict], user_id: UUID
    ) -> None:
        if conflict is None or user_id not in (
            conflict.creator_id,
            conflict.partner_id,
        ):
            raise ConflictError("Conflict not found")

    def _to_conflict_dto_detail(self, conflict: Conflict) -> ConflictDetailDTO:
        items: list[dict] = [
            self._to_item_dto(item).to_dict() for item in conflict.items
        ]
        events: list[dict] = [
            self._to_event_dto(event).to_dict() for event in conflict.events
        ]

        return ConflictDetailDTO(
            id=conflict.id,
            creator_id=conflict.creator_id,
            partner_id=conflict.partner_id,
            title=conflict.title,
            status=conflict.status,
            slug=conflict.slug,
            progress=conflict.progress,
            created_at=conflict.created_at,
            resolved_at=conflict.resolved_at,
            truce_status=conflict.truce_status,
            truce_initiator_id=conflict.truce_initiator_id,
            items=items,
            events=events,
        )

    def _to_item_dto(self, item: ConflictItem) -> ConflictItemDTO:
        return ConflictItemDTO(
            id=item.id,
            title=item.title,
            creator_choice_value=item.creator_choice_value,
            partner_choice_value=item.partner_choice_value,
            agreed_choice_value=item.agreed_choice_value,
            is_agreed=item.is_agreed,
        )

    def _to_event_dto(self, event: ConflictEvent) -> ConflictEventDTO:
        return ConflictEventDTO(
            id=event.id,
            event_type=event.event_type,
            created_at=event.created_at,
            initiator=event.initiator,
            item_id=event.item_id,
            old_value=event.old_value,
            new_value=event.new_value,
        )
