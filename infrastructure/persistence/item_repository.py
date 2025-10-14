from core.entities.conflict_item import ConflictItem
from core.interfaces.item_interface import ItemRepository
from apps.conflicts.models import ConflictItemModel
from typing import Optional
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from uuid import UUID


class DjangotItemRepository(ItemRepository):

    async def save(self, item: ConflictItem) -> ConflictItem:
        django_item, _ = await database_sync_to_async(
            ConflictItemModel.objects.update_or_create
        )(
            id=item.id,
            defaults={
                "conflict_id": item.conflict_id,
                "title": item.title,
                "creator_choice_value": item.creator_choice_value,
                "partner_choice_value": item.partner_choice_value,
                "agreed_choice_value": item.agreed_choice_value,
                "is_agreed": item.is_agreed,
            },
        )
        return self._to_entity(django_item)

    async def get_by_id_and_conflict_id(
        self, item_id: UUID, conflict_id: UUID
    ) -> Optional[ConflictItem]:
        try:
            django_item = await database_sync_to_async(ConflictItemModel.objects.get)(
                id=item_id, conflict_id=conflict_id
            )
            return self._to_entity(django_item)
        except ObjectDoesNotExist:
            return None

    def _to_entity(self, django_item: ConflictItemModel) -> ConflictItem:
        return ConflictItem(
            id=django_item.id,
            conflict_id=django_item.conflict_id,  # type: ignore
            title=django_item.title,
            creator_choice_value=django_item.creator_choice_value,
            partner_choice_value=django_item.partner_choice_value,
            agreed_choice_value=django_item.agreed_choice_value,
            is_agreed=django_item.is_agreed,
        )
