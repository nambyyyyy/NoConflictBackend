from core.entities.conflict_event import ConflictEvent
from core.interfaces.event_interface import EventRepository
from apps.conflicts.models import ConflictEventModel
from uuid import UUID
from typing import Optional


class DjangoEventRepository(EventRepository):

    async def save(
        self,
        conflict_id: UUID,
        event_type: str,
        user_id: Optional[UUID] = None,
        item_id: Optional[UUID] = None,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
    ) -> ConflictEvent:
        django_event = await ConflictEventModel.objects.acreate(
            conflict_id=conflict_id,
            item_id=item_id,
            initiator_id=user_id,
            event_type=event_type,
            old_value=old_value,
            new_value=new_value,
        )

        return self._to_entity(django_event)

    def _to_entity(self, django_event: ConflictEventModel) -> ConflictEvent:
        return ConflictEvent(
            id=django_event.id,
            conflict_id=django_event.conflict_id,
            created_at=django_event.created_at,
            initiator=(
                {
                    "id": django_event.initiator.id,
                    "username": django_event.initiator.username,
                }
                if django_event.initiator
                else None
            ),
            event_type=django_event.event_type,
            item_id=django_event.item_id if django_event.item_id else None,
            old_value=django_event.old_value if django_event.old_value else None,
            new_value=django_event.new_value if django_event.new_value else None,
        )
