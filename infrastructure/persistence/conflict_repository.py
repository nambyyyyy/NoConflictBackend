from core.entities.conflict import Conflict
from core.entities.conflict_item import ConflictItem
from core.entities.conflict_event import ConflictEvent
from core.interfaces.conflict_interface import ConflictRepository
from apps.conflicts.models import ConflictModel, ConflictItemModel, ConflictEventModel
from apps.accounts.models import UserModel
from typing import Optional


class DjangoConflictRepository(ConflictRepository):

    def get_by_id(self, conflict_id: int) -> Optional[Conflict]:
        try:
            django_conflict = ConflictModel.objects.get(id=conflict_id)
            return self._to_entity(django_conflict)
        except ConflictModel.DoesNotExist:
            return None

    def save(
        self,
        conflict: Conflict,
        creator: UserModel,
        partner: Optional[UserModel] = None,
        truce_initiator: Optional[UserModel] = None,
    ) -> Conflict:
        django_conflict, created = ConflictModel.objects.update_or_create(
            id=conflict.id,
            defaults={
                "creator": creator,
                "partner": partner,
                "title": conflict.title,
                "status": conflict.status,
                "slug": conflict.slug,
                "progress": conflict.progress,
                "resolved_at": conflict.resolved_at,
                "deleted_by_creator": conflict.deleted_by_creator,
                "deleted_by_partner": conflict.deleted_by_partner,
                "truce_status": conflict.truce_status,
                "truce_initiator": truce_initiator,
            },
        )
        if created:
            items: list[ConflictItemModel] = self._create_conflict_items(
                django_conflict, conflict.items
            )
            events: list[ConflictEventModel] = self._create_conflict_events(
                django_conflict, items
            )
            if items and events:
                ConflictEventModel.objects.create(
                    conflict=django_conflict,
                    initiator=django_conflict.creator,
                    event_type="conflict_create",
                )
        return self._to_entity(django_conflict)

    def _create_conflict_items(
        self, django_conflict: ConflictModel, items: list[dict]
    ) -> list[ConflictItemModel]:

        result = [
            ConflictItemModel.objects.create(
                conflict=django_conflict,
                title=item["title"],
                creator_choice_value=item["creator_choice_value"],
            )
            for item in items
        ]

        return result

    def _create_conflict_events(
        self, django_conflict: ConflictModel, items: list[ConflictItemModel]
    ) -> list[ConflictEventModel]:
        result = [
            ConflictEventModel.objects.create(
                conflict=django_conflict,
                item=item,
                initiator=django_conflict.creator,
                event_type="item_add",
                new_value=item.creator_choice_value,
            )
            for item in items
        ]
        return result

    def _to_entity(self, django_conflict: ConflictModel) -> Conflict:
        """Приватный метод конвертации"""
        items_data = [
            ConflictItem(
                id=item.id,
                conflict_id=django_conflict.id,
                title=item.title,
                creator_choice_value=item.creator_choice_value,
                partner_choice_value=item.partner_choice_value,
                agreed_choice_value=item.agreed_choice_value,
                is_agreed=item.is_agreed,
            )
            for item in django_conflict.items.all()
        ]

        events_data = [
            ConflictEvent(
                id=event.id,
                conflict_id=django_conflict.id,
                created_at=event.created_at,
                initiator={
                    "id": event.initiator.id,
                    "username": event.initiator.username,
                },
                event_type=event.event_type,
                item_id=event.item_id,
                old_value=event.old_value,
                new_value=event.new_value,
            )
            for event in django_conflict.events.all() # type: ignore
        ]

        return Conflict(
            id=django_conflict.id,
            creator_id=django_conflict.creator.id,
            partner_id=django_conflict.partner.id if django_conflict.partner else None,
            title=django_conflict.title,
            status=django_conflict.status,
            slug=django_conflict.slug,
            progress=django_conflict.progress,
            resolved_at=django_conflict.resolved_at,
            deleted_by_creator=django_conflict.deleted_by_creator,
            deleted_by_partner=django_conflict.deleted_by_partner,
            truce_status=django_conflict.truce_status,
            truce_initiator_id=(
                django_conflict.truce_initiator.id
                if django_conflict.truce_initiator
                else None
            ),
            items=items_data,
            events=events_data,
        )
