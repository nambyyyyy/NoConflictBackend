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
from datetime import datetime, timezone
from dataclasses import asdict


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
        items_entitys: list[ConflictItem] = [
            ConflictItem(
                id=item.get("id"),  # type: ignore
                conflict_id=conflict_entity.id,
                title=item.get("title"),  # type: ignore
                creator_choice_value=item.get("creator_choice_value"),
            )
            for item in items
        ]
        saved_events: list[ConflictEvent] = []
        event_entity: ConflictEvent = ConflictEvent(
            conflict_id=conflict_entity.id,
            event_type="conflict_create",
            initiator_id=conflict_entity.creator_id,
            initiator_username=conflict_entity.creator_username,
        )
        saved_events.append(event_entity)

        for item in items_entitys:
            saved_events.append(
                ConflictEvent(
                    conflict_id=conflict_entity.id,
                    event_type="item_add",
                    item_id=item.id,
                    item_title=item.title,
                    initiator_id=conflict_entity.creator_id,
                    initiator_username=conflict_entity.creator_username,
                )
            )

        async with transaction_atomic():
            for event in saved_events:
                await self.event_repo.save(event)
            for item in items_entitys:
                await self.item_repo.save(item)
            saved_conflict: Conflict = await self.conflict_repo.save(conflict_entity)  # type: ignore

            conflict_dto: ConflictDetailDTO = self._to_conflict_dto_detail(
                saved_conflict
            )
            return conflict_dto.to_dict()

    async def get_conflict(self, user_id: UUID, slug: str) -> dict[str, Any]:
        conflict_entity: Conflict = await self.conflict_repo.get_by_slug(slug)
        self.conflict_valid.validate_access_conflict(conflict_entity, user_id)
        self.conflict_valid.validate_delete_conflict(conflict_entity, user_id)
        return self._to_conflict_dto_detail(conflict_entity).to_dict()

    async def cancel_conflict(
        self,
        user_id: UUID,
        slug: str,
        transaction_atomic: Callable,
        channel_layer: Callable,
    ) -> dict[str, Any]:
        async with transaction_atomic():
            conflict_entity: Optional[Conflict] = await self.conflict_repo.get_by_slug(
                slug
            )
            self.conflict_valid.validate_access_conflict(conflict_entity, user_id)

            event_entity: ConflictEvent = ConflictEvent(
                conflict_id=conflict_entity.id,
                event_type="conflict_cancel",
                initiator_id=user_id,
                initiator_username=(
                    conflict_entity.creator_username
                    if conflict_entity.partner_username == user_id
                    else conflict_entity.partner_username
                ),
            )
            await self.event_repo.save(event_entity)

            conflict_entity.status = "cancelled"
            conflict_entity.resolved_at = datetime.now(timezone.utc)

            saved_conflict: Conflict = await self.conflict_repo.save(
                conflict_entity, update_fields=["status", "resolved_at"]
            )  # type: ignore

        await channel_layer().group_send(
            f"conflict_{slug}",
            {
                "type": "conflict.cancelled",
                "status": "cancelled",
                "progress": saved_conflict.progress,
                "resolved_at": saved_conflict.resolved_at.isoformat(),  # type: ignore
                "initiator_id": event_entity.initiator_id,
                "initiator_username": event_entity.initiator_username,
            },
        )
        conflict_dto: ConflictShortDTO = self._to_conflict_dto_schort(saved_conflict)
        return conflict_dto.to_dict()

    async def delete_conflict(
        self, user_id: UUID, slug: str, transaction_atomic: Callable
    ):
        with transaction_atomic():
            conflict_entity: Optional[Conflict] = await self.conflict_repo.get_by_slug(
                slug
            )
            self.conflict_valid.validate_access_conflict(conflict_entity, user_id)
            self.conflict_valid.validate_delete_conflict(conflict_entity, user_id)

            if user_id == conflict_entity.creator_id:
                conflict_entity.deleted_by_creator = True

            elif user_id == conflict_entity.partner_id:
                conflict_entity.deleted_by_partner = True

            if (
                conflict_entity.deleted_by_creator
                and conflict_entity.deleted_by_partner
            ):
                conflict_entity.is_deleted = True
                conflict_entity.resolved_at = datetime.now(timezone.utc)

            await self.conflict_repo.save(
                conflict_entity,
                update_fields=[
                    "deleted_by_creator",
                    "deleted_by_partner",
                    "is_deleted",
                    "resolved_at",
                ],
                return_none=True,
            )

    async def create_offer_truce(
        self,
        user_id: UUID,
        slug: str,
        transaction_atomic: Callable,
        channel_layer: Callable,
    ) -> dict[str, Any]:
        conflict_dto: ConflictDetailDTO = await self._update_offer_truce(
            user_id, slug, transaction_atomic, channel_layer, "none", "pending"
        )
        return conflict_dto.to_dict()

    async def cancel_offer_truce(
        self,
        user_id: UUID,
        slug: str,
        transaction_atomic: Callable,
        channel_layer: Callable,
    ) -> dict[str, Any]:
        conflict_dto: ConflictDetailDTO = await self._update_offer_truce(
            user_id, slug, transaction_atomic, channel_layer, "pending", "none"
        )
        return conflict_dto.to_dict()

    async def accepted_offer_truce(
        self,
        user_id: UUID,
        slug: str,
        transaction_atomic: Callable,
        channel_layer: Callable,
    ) -> dict[str, Any]:
        conflict_dto: ConflictDetailDTO = await self._update_offer_truce(
            user_id, slug, transaction_atomic, channel_layer, "pending", "accepted"
        )
        return conflict_dto.to_dict()

    async def update_item(
        self,
        event_type: str,
        user_id: UUID,
        slug: str,
        item_id: UUID,
        item_title: str,
        new_value: str,
        transaction_atomic: Callable,
    ) -> dict[str, Any]:
        self.conflict_valid.validate_item_update(
            event_type, user_id, slug, item_id, new_value
        )
        async with transaction_atomic():
            conflict: Conflict = await self.conflict_repo.get_by_slug(slug)
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

            event_entity: ConflictEvent = ConflictEvent(
                conflict_id=conflict.id,
                event_type=event_type,
                initiator_id=(
                    conflict.creator_id
                    if conflict.creator_id == user_id
                    else conflict.partner_id
                ),
                initiator_username=(
                    conflict.creator_username
                    if conflict.creator_id == user_id
                    else conflict.partner_username
                ),
                item_id=item_id,
                item_title=item_title,
                old_value=old_value,
                new_value=new_value,
            )

            await self.event_repo.save(event_entity)

            if (item.creator_choice_value and item.partner_choice_value) and (
                item.creator_choice_value == item.partner_choice_value
            ):
                item.agreed_choice_value = item.creator_choice_value
                item.is_agreed = True

                self._update_progress(conflict, item.id)
                event_entity: ConflictEvent = ConflictEvent(
                    conflict_id=conflict.id,
                    event_type="conflict_resolved",
                )
                await self.event_repo.save(event_entity)
                conflict: Conflict = await self.conflict_repo.save(
                    conflict, update_fields=["progress", "status", "resolved_at"]
                )  # type: ignore

            await self.item_repo.save(
                item,
                update_fields=[
                    "creator_choice_value",
                    "partner_choice_value",
                    "agreed_choice_value",
                    "is_agreed",
                ],
            )
            if item.is_agreed:
                conflict_dto: ConflictDetailDTO = self._to_conflict_dto_detail(conflict)
                return conflict_dto.to_dict()
            else:
                item_dto: ConflictItemDTO = self._to_item_dto(item)
                return item_dto.to_dict()

    async def _update_offer_truce(
        self,
        user_id: UUID,
        slug: str,
        transaction_atomic: Callable,
        channel_layer: Callable,
        old_truce_status: str,
        new_truce_status: str,
    ) -> ConflictDetailDTO:
        async with transaction_atomic():
            conflict_entity: Optional[Conflict] = await self.conflict_repo.get_by_slug(
                slug
            )
            self.conflict_valid.validate_access_conflict(conflict_entity, user_id)

            event_entity: ConflictEvent = ConflictEvent(
                conflict_id=conflict_entity.id,
                event_type="truce_offer",
                initiator_id=user_id,
                initiator_username=(
                    conflict_entity.creator_username
                    if conflict_entity.creator_id == user_id
                    else conflict_entity.partner_username
                ),
                old_value=old_truce_status,
                new_value=new_truce_status,
            )
            await self.event_repo.save(event_entity)

            conflict_entity.truce_status = new_truce_status
            conflict_entity.truce_initiator_id = user_id
            conflict_entity.truce_initiator_username = (
                conflict_entity.creator_username
                if user_id == conflict_entity.creator_id
                else conflict_entity.partner_username
            )
            saved_conflict: Conflict = await self.conflict_repo.save(
                conflict_entity,
                update_fields=[
                    "truce_status",
                    "truce_initiator_id",
                ],
            )  # type: ignore

            await channel_layer().group_send(
                f"conflict_{slug}",
                {
                    "type": "conflict.truce_offer",
                    "truce_status": event_entity.new_value,
                    "initiator_id": event_entity.initiator_id,
                    "initiator_username": event_entity.initiator_username,
                },
            )
            return self._to_conflict_dto_detail(saved_conflict)

    def _update_progress(self, conflict: Conflict, item_id: UUID) -> None:
        for index, item in enumerate(conflict.items):
            if item.id == item_id:
                conflict.items[index] = item
                break

        total_items = len(conflict.items)
        agreed_count = sum(1 for item in conflict.items if item.is_agreed)
        conflict.progress = (
            round((agreed_count / total_items) * 100, 2) if total_items else 0.0
        )
        if conflict.progress >= 100:
            conflict.status = "resolved"
            conflict.resolved_at = datetime.now(timezone.utc)

    def _to_conflict_dto_detail(self, conflict: Conflict) -> ConflictDetailDTO:
        data = asdict(conflict)
        data["items"] = [self._to_item_dto(i).to_dict() for i in conflict.items]
        data["events"] = [self._to_event_dto(e).to_dict() for e in conflict.events]
        return ConflictDetailDTO(**data)

    def _to_conflict_dto_schort(self, conflict: Conflict) -> ConflictShortDTO:
        ALLOWED_FIELDS = {
            "id",
            "creator_id",
            "creator_username",
            "partner_id",
            "partner_username",
            "title",
            "status",
            "progress",
            "resolved_at",
        }
        return self._build_dto(ConflictShortDTO, conflict, ALLOWED_FIELDS)

    def _to_item_dto(self, item: ConflictItem) -> ConflictItemDTO:
        ALLOWED_FIELDS = {
            "id",
            "title",
            "creator_choice_value",
            "partner_choice_value",
            "agreed_choice_value",
            "is_agreed",
        }
        return self._build_dto(ConflictItemDTO, item, ALLOWED_FIELDS)

    def _to_event_dto(self, event: ConflictEvent) -> ConflictEventDTO:
        ALLOWED_FIELDS = {
            "id",
            "event_type",
            "created_at",
            "initiator_id",
            "initiator_username",
            "item_id",
            "item_title",
            "old_value",
            "new_value",
        }
        return self._build_dto(ConflictEventDTO, event, ALLOWED_FIELDS)

    def _build_dto(self, dto, entity, allowed_fields: set[str]):
        data = asdict(entity)
        filtered = {k: v for k, v in data.items() if k in allowed_fields}
        return dto(**filtered)
