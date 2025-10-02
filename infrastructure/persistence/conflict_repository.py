from uuid import UUID
from core.entities.conflict import Conflict
from core.entities.option_choice import OptionChoice
from core.interfaces.conflict_interface import ConflictRepository, OptionChoicRepository
from apps.conflicts.models import ConflictModel, OptionChoiceModel
from apps.accounts.models import UserModel
from typing import Optional


class DjangoConflictRepository(ConflictRepository):

    def get_by_id(self, conflict_id: int) -> Optional[Conflict]:
        try:
            django_conflict = ConflictModel.objects.get(id=conflict_id)
            return self._to_entity(django_conflict)
        except ConflictModel.DoesNotExist:
            return None

    def save(self, conflict: Conflict) -> Optional[Conflict]:
        condition = []

        if conflict.partner_id:
            condition.append(conflict.partner_id)
        if conflict.truce_initiator_id:
            condition.append(conflict.truce_initiator_id)

        condition.append(conflict.creator_id)
        try:
            users = UserModel.objects.in_bulk(condition)
            creator = users.get(conflict.creator_id)
            if creator is None:
                return None

            partner = users.get(conflict.partner_id) if conflict.partner_id else None
            truce_initiator = (
                users.get(conflict.truce_initiator_id)
                if conflict.truce_initiator_id
                else None
            )
        except Exception:
            return None

        # Создаем или обновляем
        django_conflict, _ = ConflictModel.objects.update_or_create(
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
        # Создать item и options в БД, связать с конфликтом
        # for item in conflict.items:
            
        
        return self._to_entity(django_conflict)

    def _to_entity(self, django_conflict: ConflictModel) -> Conflict:
        """Приватный метод конвертации"""
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
        )


# Набор опций для каждого пункта в конфликте
class DjangoOptionChoicRepository(OptionChoicRepository):

    def get_many(self, option_ids: list[UUID]) -> list[OptionChoice]:

        options_dict = OptionChoiceModel.objects.in_bulk(option_ids)

        options = [
            self._to_entity(options_dict[oid])
            for oid in option_ids
            if oid in options_dict
        ]
        return options
 

    def _to_entity(self, django_options_conflict: OptionChoiceModel) -> OptionChoice:
        """Приватный метод конвертации"""
        return OptionChoice(
            id=django_options_conflict.id,
            value=django_options_conflict.value,
            is_predefined=django_options_conflict.is_predefined,
        )
