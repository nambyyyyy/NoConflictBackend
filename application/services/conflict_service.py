from core.interfaces.conflict_interface import (
    ConflictRepository,
)
from core.interfaces.item_interface import ItemRepository
from core.interfaces.event_interface import EventRepository
from application.dtos.conflict_dto import (
    ConflictDetailDTO,
    ConflictItemDTO,
    ConflictEventDTO,
    ConflictShortDTO,
)
from core.entities.conflict import Conflict, ConflictError
from core.entities.conflict_item import ConflictItem
from core.entities.conflict_event import ConflictEvent
from application.validators.conflict_validator import ConflictValidator
from typing import Optional, Callable, Any
from uuid import UUID


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
        self.conflict_valid = ConflictValidator()

    async def create_conflict(
        self,
        creator_id: UUID,
        partner_id: Optional[UUID],
        title: str,
        items: list[dict],
        transaction_atomic: Callable,
    ) -> dict[str, Any]:

        self.conflict_valid.validate_conflict_registration(
            creator_id, partner_id, title, items
        )

        conflict_entity: Conflict = Conflict(
            creator_id=creator_id, partner_id=partner_id, title=title
        )
        items_entity: list[ConflictItem] = [
            ConflictItem(
                id=item.get("id"),  # type: ignore
                conflict_id=conflict_entity.id,
                title=item.get("title"),  # type: ignore
                creator_choice_value=item.get("creator_choice_value"),
            )
            for item in items
        ]

        with transaction_atomic():
            saved_conflict: Conflict = self.conflict_repo.save(conflict_entity)
            saved_items: list[ConflictItem] = [
                await self.item_repo.save(item) for item in items_entity
            ]

            saved_events: list[ConflictEvent] = []
            event_create = await self.event_repo.save(
                conflict_id=saved_conflict.id,
                event_type="conflict_create",
                user_id=saved_conflict.creator_id,
            )
            saved_events.append(event_create)

            for item in saved_items:
                saved_events.append(
                    await self.event_repo.save(
                        conflict_id=saved_conflict.id,
                        event_type="item_add",
                        user_id=saved_conflict.creator_id,
                        item_id=item.id,
                        new_value=item.creator_choice_value,
                    )
                )

            saved_conflict.items = saved_items
            saved_conflict.events = saved_events

            return self._to_conflict_dto_detail(saved_conflict).to_dict()

    async def get_conflict(self, user_id: UUID, slug: str) -> dict[str, Any]:
        conflict_entity: Optional[Conflict] = await self.conflict_repo.get_by_slug(slug)
        self.conflict_valid.validate_access_conflict(conflict_entity, user_id)
        return self._to_conflict_dto_detail(conflict_entity).to_dict()

    async def cancel_conflict(
        self, user_id: UUID, slug: str, transaction_atomic: Callable
    ) -> dict[str, Any]:
        with transaction_atomic():
            conflict_entity: Optional[Conflict] = await self.conflict_repo.get_by_slug(
                slug
            )
            self.conflict_valid.validate_access_conflict(conflict_entity, user_id)
            conflict_entity.status = "cancelled"
            saved_conflict: Conflict = self.conflict_repo.save(
                conflict_entity, update_fields=["status", "resolved_at"]
            )
            await self.event_repo.save(
                conflict_id=saved_conflict.id,
                event_type="conflict_cancel",
                user_id=user_id,
            )
            return self._to_conflict_dto_schort(saved_conflict).to_dict()

    async def update_item(
        self,
        event_type: str,
        user_id: UUID,
        slug: str,
        item_id: UUID,
        new_value: str,
        transaction_atomic: Callable,
    ) -> dict[str, Any]:
        self.conflict_valid.validate_item_update(
            event_type, user_id, slug, item_id, new_value
        )

        with transaction_atomic():
            conflict: Optional[Conflict] = await self.conflict_repo.get_by_slug(slug)
            self.conflict_valid.validate_access_conflict(conflict, user_id)

            item: Optional[ConflictItem] = (
                await self.item_repo.get_by_id_and_conflict_id(item_id, conflict.id)
            )

            if item is None:
                raise ConflictError("Item Not Found")

            if user_id == conflict.creator_id:
                old_value = item.creator_choice_value
                item.creator_choice_value = new_value
            else:
                old_value = item.partner_choice_value
                item.partner_choice_value = new_value

            await self.event_repo.save(
                conflict_id=conflict.id,
                event_type=event_type,
                user_id=user_id,
                item_id=item.id,
                old_value=old_value,
                new_value=new_value,
            )

            if (item.creator_choice_value and item.partner_choice_value) and (
                item.creator_choice_value == item.partner_choice_value
            ):
                item.agreed_choice_value = item.creator_choice_value
                item.is_agreed = True

            await self.item_repo.save(item)
            return self._to_item_dto(item).to_dict()

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

    def _to_conflict_dto_schort(self, conflict: Conflict) -> ConflictShortDTO:
        return ConflictShortDTO(
            id=conflict.id,
            creator_id=conflict.creator_id,
            partner_id=conflict.partner_id,
            title=conflict.title,
            status=conflict.status,
            progress=conflict.progress,
            resolved_at=conflict.resolved_at,
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
