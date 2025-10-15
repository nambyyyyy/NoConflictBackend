from core.entities.conflict_event import ConflictEvent
from core.interfaces.event_interface import EventRepository
from apps.conflicts.models import ConflictEventModel
from uuid import UUID
from typing import Optional


class DjangoEventRepository(EventRepository):

    async def save(self, event: ConflictEvent) -> ConflictEvent:
        django_event = await ConflictEventModel.objects.acreate(
            conflict_id=event.conflict_id,
            item_id=event.item_id,
            initiator_id=event.initiator_id,
            event_type=event.event_type,
            old_value=event.old_value,
            new_value=event.new_value,
        )
        django_event_with_initiator = await ConflictEventModel.objects.select_related(
            "initiator"
        ).aget(id=django_event.id)

        return self._to_entity(django_event_with_initiator)

    def _to_entity(self, django_event: ConflictEventModel) -> ConflictEvent:
        return ConflictEvent(
            id=django_event.id,
            conflict_id=django_event.conflict_id,
            created_at=django_event.created_at,
            initiator_id=(
                django_event.initiator.id if django_event.initiator.id else None
            ),
            initiator_username=(
                django_event.initiator.username
                if django_event.initiator.username
                else None
            ),
            event_type=django_event.event_type,
            item_id=django_event.item_id if django_event.item_id else None,
            old_value=django_event.old_value if django_event.old_value else None,
            new_value=django_event.new_value if django_event.new_value else None,
        )
