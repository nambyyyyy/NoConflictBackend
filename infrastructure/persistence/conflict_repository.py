from core.entities.conflict import Conflict
from core.entities.conflict_item import ConflictItem
from core.entities.conflict_event import ConflictEvent
from core.interfaces.conflict_interface import ConflictRepository
from apps.conflicts.models import ConflictModel
from typing import Optional
from uuid import UUID
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist


class DjangoConflictRepository(ConflictRepository):

    def get_by_id(self, conflict_id: UUID) -> Optional[Conflict]:
        try:
            django_conflict = ConflictModel.objects.get(id=conflict_id)
            return self._to_entity_conflict(django_conflict)
        except ConflictModel.DoesNotExist:
            return None

    async def get_by_slug(self, slug: str) -> Optional[Conflict]:
        try:
            django_conflict = await database_sync_to_async(ConflictModel.objects.get)(
                slug=slug
            )
            return self._to_entity_conflict(django_conflict)
        except ObjectDoesNotExist:
            return None

    def save(
        self,
        conflict: Conflict,
        update_fields: Optional[list[str]] = None,
    ) -> Conflict:
        if update_fields is None:
            defaults = {
                "creator_id": conflict.creator_id,
                "partner_id": conflict.partner_id,
                "title": conflict.title,
                "status": conflict.status,
                "slug": conflict.slug,
                "progress": conflict.progress,
                "resolved_at": conflict.resolved_at,
                "deleted_by_creator": conflict.deleted_by_creator,
                "deleted_by_partner": conflict.deleted_by_partner,
                "truce_status": conflict.truce_status,
                "truce_initiator_id": conflict.truce_initiator_id,
            }
        else:
            defaults = {field: getattr(conflict, field) for field in update_fields}

        django_conflict, _ = ConflictModel.objects.update_or_create(
            id=conflict.id, defaults=defaults
        )

        return self._to_entity_conflict(django_conflict)

    def _to_entity_items(self, django_conflict: ConflictModel) -> list[ConflictItem]:
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
            for item in django_conflict.items.all()  # type: ignore
        ]
        return items_data

    def _to_entity_events(self, django_conflict: ConflictModel) -> list[ConflictEvent]:
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
            for event in django_conflict.events.all()  # type: ignore
        ]
        return events_data

    def _to_entity_conflict(self, django_conflict: ConflictModel) -> Conflict:
        """Приватный метод конвертации"""

        return Conflict(
            id=django_conflict.id,
            creator_id=django_conflict.creator.id,
            partner_id=django_conflict.partner.id if django_conflict.partner else None,
            title=django_conflict.title,
            status=django_conflict.status,
            slug=django_conflict.slug,
            progress=django_conflict.progress,
            created_at=django_conflict.created_at,
            resolved_at=django_conflict.resolved_at,
            deleted_by_creator=django_conflict.deleted_by_creator,
            deleted_by_partner=django_conflict.deleted_by_partner,
            truce_status=django_conflict.truce_status,
            truce_initiator_id=(
                django_conflict.truce_initiator.id
                if django_conflict.truce_initiator
                else None
            ),
            items=self._to_entity_items(django_conflict),
            events=self._to_entity_events(django_conflict),
        )
