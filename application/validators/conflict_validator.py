from typing import Optional
from uuid import UUID
from core.entities.conflict import Conflict, ConflictError


class ConflictValidator:

    def validate_conflict_registration(
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

        self.validate_items_registration(items)

    def validate_items_registration(self, items: Optional[list]) -> None:
        if not items:
            raise ConflictError("Для создания конфликта нужен минимум один пункт")

        for item in items:
            if not item["id"]:
                raise ConflictError("У item нет id")
            if not item["title"]:
                raise ConflictError("У item нет title")
            if not item["creator_choice_value"]:
                raise ConflictError("У item нет creator_choice_value")

    def validate_item_update(
        self, event_type: str, user_id: UUID, slug: str, item_id: UUID, new_value: str
    ):
        if not event_type or not isinstance(event_type, str):
            raise ValueError("Event type is required and must be a string")

        if not slug or not isinstance(slug, str):
            raise ValueError("Conflict slug is required and must be a string")

        if not new_value or not isinstance(new_value, str):
            raise ValueError("New value is required and must be a non-empty string")

        if not item_id:
            raise ValueError("Item ID is required")

        if not user_id:
            raise ValueError("User ID is required")

    def validate_access_conflict(
        self, conflict: Optional[Conflict], user_id: UUID
    ) -> None:
        if conflict is None or user_id not in (
            conflict.creator_id,
            conflict.partner_id,
        ):
            raise ConflictError("Conflict not found")
