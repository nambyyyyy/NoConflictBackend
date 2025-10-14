from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4, UUID
from core.entities.conflict_item import ConflictItem
from core.entities.conflict_event import ConflictEvent

class ConflictError(Exception):
    """Любая доменная ошибка по конфликтам."""


@dataclass
class Conflict:
    title: str
    creator_id: UUID
    partner_id: Optional[UUID] = None 
    
    id: UUID = field(default_factory=uuid4)
    status: str = "pending"  # pending / in_progress / resolved / cancelled / abandoned
    slug: str = field(default_factory=lambda: str(uuid4()))

    progress: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None

    deleted_by_creator: bool = False
    deleted_by_partner: bool = False

    truce_status: str = "none"  # none / pending / accepted
    truce_initiator_id: Optional[UUID] = None

    items: list["ConflictItem"] = field(default_factory=list)
    events: list["ConflictEvent"] = field(default_factory=list)
    
    # СТАРЫЕ МЕТОДЫ МОДЕЛИ ВЗЯТЫЕ ИЗ ПРОШЛОЙ АРХИТЕКТУРЫ
    # НЕ АКТУАЛЬНЫЕ, ИСПОЛЬЗОВАТЬ ТОЛЬКО ДЛЯ ОРИЕНТИРА. 

    # def add_partner(self, user_id: int):
    #     if self.partner_id is not None:
    #         raise ConflictError("Партнер уже назначен.")
    #     if user_id == self.creator_id:
    #         raise ConflictError("Нельзя быть партнером самому себе.")
    #     self.partner_id = user_id
    #     self.status = "in_progress"

    # def resolve(self, manual=False):
    #     if manual or self.progress >= 100:
    #         self.status = "resolved"
    #         self.resolved_at = datetime.now()
    #     else:
    #         raise ConflictError(
    #             "Нельзя завершить без 100% прогресса, если не manually."
    #         )

    # def cancel(self):
    #     if self.status in ("cancelled", "abandoned", "resolved"):
    #         raise ConflictError("Конфликт завершён, отменён или заброшен.")
    #     self.status = "cancelled"

    # def unlock_item(self, item_id: UUID):
    #     if self.status in ("resolved", "cancelled", "abandoned"):
    #         raise ConflictError(
    #             "Нельзя изменять пункты в завершенном или отмененном конфликте."
    #         )

    #     item = next(item for item in self.items if item.id == item_id)
    #     item.unlock()

    # def soft_delete_for_user(self, user_id: int):
    #     if user_id == self.creator_id:
    #         if self.deleted_by_creator:
    #             raise ConflictError("Конфликт уже удален этим пользователем.")
    #         self.deleted_by_creator = True
    #     elif self.partner_id and user_id == self.partner_id:
    #         if self.deleted_by_partner:
    #             raise ConflictError("Конфликт уже удален этим пользователем.")
    #         self.deleted_by_partner = True
    #     else:
    #         raise ConflictError("User не участник этого конфликта.")

    # def can_propose_truce(self, user_id: int, all_items_answered: bool) -> None:
    #     """
    #     Валидируем, можно ли текущему пользователю предложить перемирие.
    #     Аргументы:
    #       - user_id: кто предлагает
    #       - all_items_answered: заполнены ли обеими сторонами все пункты
    #     """
    #     if user_id not in (self.creator_id, self.partner_id):
    #         raise ConflictError("Вы не участник.")
    #     if not (self.creator_id and self.partner_id):
    #         raise ConflictError("В конфликте не все участники.")
    #     if self.status != "in_progress":
    #         raise ConflictError("Конфликт уже завершен, отменен или не начат.")
    #     if self.truce_status == "pending":
    #         raise ConflictError("Предложение уже отправлено.")
    #     if not all_items_answered:
    #         raise ConflictError("Не все пункты анкеты заполнены обоими участниками.")

    # def get_django_field_values(self) -> dict:
    #     """Получить значения полей для Django ORM"""
    #     return {
    #         "creator_id": self.creator_id,
    #         "partner_id": self.partner_id,
    #         "title": self.title or "",
    #         "status": self.status,
    #         "slug": self.slug,
    #         "progress": self.progress,
    #         "resolved_at": self.resolved_at,
    #         "deleted_by_creator": self.deleted_by_creator,
    #         "deleted_by_partner": self.deleted_by_partner,
    #         "truce_status": self.truce_status,
    #         "truce_initiator_id": self.truce_initiator_id,
    #         "updated_at": timezone.now(),
    #     }
