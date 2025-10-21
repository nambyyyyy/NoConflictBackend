from core.entities.conflict import Conflict
from core.entities.conflict_item import ConflictItem
from core.entities.conflict_event import ConflictEvent
from core.interfaces.conflict_interface import ConflictRepository
from apps.conflicts.models import ConflictModel, ConflictEventModel
from django.db import models
from typing import Optional
from uuid import UUID


class DjangoConflictRepository(ConflictRepository):

    async def _base_get(self, lookup_field: str, lookup_value: UUID | str) -> Conflict:
        django_conflict = await (
            ConflictModel.objects.select_related(
                "creator", "partner", "truce_initiator"
            )
            .prefetch_related(
                # Загрузить события и для каждого события загрузить initiator
                models.Prefetch(
                    "events",
                    queryset=ConflictEventModel.objects.select_related(
                        "initiator", "item"
                    ),
                ),
                "items",
            )
            .aget(**{lookup_field: lookup_value})
        )
        return self._to_entity_conflict(django_conflict)

    async def get_by_id(self, conflict_id: UUID) -> Conflict:
        return await self._base_get("id", conflict_id)

    async def get_by_slug(self, slug: str) -> Conflict:
        return await self._base_get("slug", slug)

    async def save(
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

        django_conflict, _ = await ConflictModel.objects.aupdate_or_create(
            id=conflict.id,
            defaults=defaults,
        )
        return await self._base_get("id", django_conflict.id)

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
                initiator_id=event.initiator.id if event.initiator else None,
                initiator_username=(
                    event.initiator.username if event.initiator else None
                ),
                event_type=event.event_type,
                item_id=event.item.id if event.item else None,
                item_title=event.item.title if event.item else None,
                old_value=event.old_value,
                new_value=event.new_value,
            )
            for event in django_conflict.events.all()
        ]
        return events_data

    def _to_entity_conflict(self, django_conflict: ConflictModel) -> Conflict:
        """Приватный метод конвертации"""
        return Conflict(
            id=django_conflict.id,
            creator_id=django_conflict.creator.id,
            creator_username=(
                django_conflict.creator.username
                if django_conflict.creator.username
                else None
            ),
            partner_id=django_conflict.partner.id if django_conflict.partner else None,
            partner_username=(
                django_conflict.partner.username if django_conflict.partner else None
            ),
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
            truce_initiator_username=(
                django_conflict.truce_initiator.username
                if django_conflict.truce_initiator
                else None
            ),
            items=self._to_entity_items(django_conflict),
            events=self._to_entity_events(django_conflict),
        )
