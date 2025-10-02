from core.interfaces.conflict_interface import (
    ConflictRepository,
    OptionChoicRepository,
)
from application.dtos.conflict_dto import (
    ConflictDetailDTO,
    ConflictEventDTO,
    ConflictItemDTO,
    ConflictShortDTO,
    OptionChoiceDTO,
)
from core.entities.conflict import Conflict, ConflictError
from core.entities.conflict_item import ConflictItem
from core.entities.conflict_event import ConflictEvent
from core.entities.option_choice import OptionChoice
from typing import Any, Optional
from uuid import uuid4, UUID


class ConflictService:
    def __init__(
        self,
        conflict_repository: ConflictRepository,
        option_choice_repository: OptionChoicRepository,
    ):
        self.conflict_repo = conflict_repository
        self.option_choice_repo = option_choice_repository

    def get_form_conflict(self, creator_id: UUID) -> ConflictDetailDTO:
        conflict_entity: Conflict = Conflict(
            creator_id=creator_id,
        )
        return self._to_dto_detail(conflict_entity)

    def create_conflict(
        self, creator_id, validated_data: dict[str, Any]
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

        return creator_id, partner_id, title, items, events # type: ignore

    def _validate_items(self, items: Optional[list]) -> None:
        if not items:
            raise ConflictError("Для создания конфликта нужен минимум один пункт")

        for item in items:
            item_id, item_type, available_options = (
                item.get("id"),
                item.get("item_type"),
                item.get("options"),
            )
            if not item_id:
                raise ConflictError("У item нет id")
            if not item_type:
                raise ConflictError("У item нет title")
            if not available_options:
                raise ConflictError("У item нет options")

            if not isinstance(available_options, list):
                raise ConflictError("Options должны быть списком")
            
            for opt in available_options:
                opt_id = opt.get("id")
                opt_value = opt.get("value")
                if not opt_id:
                    raise ConflictError("У опции нет id")
                if not opt_value:
                    raise ConflictError("У опции нет value")

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
            items=[self._to_item_dto(item) for item in conflict.items],
            events=[self._to_event_dto(event) for event in conflict.events],
        )

    def _to_item_dto(self, item: ConflictItem) -> ConflictItemDTO:
        options: list[OptionChoice] = self.option_choice_repo.get_many(
            item.available_option_ids
        )
        available_options = [
            OptionChoiceDTO(id=o.id, value=o.value, is_predefined=o.is_predefined)
            for o in options
        ]

        return ConflictItemDTO(
            id=item.id,
            item_type=item.item_type,
            available_options=available_options,
            creator_choice_id=item.creator_choice_id,
            partner_choice_id=item.partner_choice_id,
            agreed_choice_id=item.agreed_choice_id,
            is_agreed=item.is_agreed,
        )

    def _to_event_dto(self, event: ConflictEvent) -> ConflictEventDTO:
        return ConflictEventDTO(
            id=event.id,
            event_type=event.event_type,
            created_at=event.created_at,
            initiator_id=event.initiator_id,
            details=event.details,
        )
