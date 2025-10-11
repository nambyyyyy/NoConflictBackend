from core.entities.conflict_item import ConflictItem
from core.interfaces.item_interface import ItemRepository
from apps.conflicts.models import ConflictItemModel


class DjangotItemRepository(ItemRepository):

    def save(self, item: ConflictItem) -> ConflictItem:
        django_item, _ = ConflictItemModel.objects.update_or_create(
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

    def _to_entity(self, django_item: ConflictItemModel) -> ConflictItem:
        return ConflictItem(
            id=django_item.id,
            conflict_id=django_item.conflict_id, # type: ignore
            title=django_item.title,
            creator_choice_value=django_item.creator_choice_value,
            partner_choice_value=django_item.partner_choice_value,
            agreed_choice_value=django_item.agreed_choice_value,
            is_agreed=django_item.is_agreed,
        )
