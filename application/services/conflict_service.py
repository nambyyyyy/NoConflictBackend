from backend.core.interfaces.conflict_interface import (
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
from core.entities.conflict import Conflict
from core.entities.conflict_item import ConflictItem
from core.entities.conflict_event import ConflictEvent
from core.entities.option_choice import OptionChoice
from typing import Any




class ConflictService:
    def __init__(
        self,
        conflict_repository: ConflictRepository,
        option_choice_repository: OptionChoicRepository,
    ):
        self.conflict_repo = conflict_repository
        self.option_choice_repo = option_choice_repository

    def create_conflict(
        self, creator_id: int, validated_data: dict[str, Any]
    ) -> ConflictDetailDTO:
        conflict_entity: Conflict = Conflict(creator_id=creator_id, **validated_data)
        saved_conflict: Conflict = self.conflict_repo.save(conflict_entity)
        return self._to_dto_detail(saved_conflict)

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
