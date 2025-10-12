from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.exceptions import ValidationError
import uuid
from apps.common.models import IsDeletedModel, BaseModel
from django.utils import timezone

User = get_user_model()  


class ConflictModel(IsDeletedModel):
    STATUS_CHOICES = [
        ("pending", "Ожидает партнера"),  # Когда создан без партнёра
        ("in_progress", "В процессе"),  # Когда оба пользователя присоединены
        ("resolved", "Разрешен"),  # Полностью согласован или manually завершён
        ("cancelled", "Отменен"),  # Отказ от продолжения
        (
            "abandoned",
            "Заброшен",
        ),  # Заброшен. Вызывается отдельно скриптом в случае истечения срока действия.
    ]

    # Статусы предложения примирения
    TRUCE_STATUS_CHOICES = [
        ("none", "Нет предложения"),
        ("pending", "Ожидает ответа"),
        ("accepted", "Принято"),
    ]

    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_conflicts"
    )  # User A (создатель)
    partner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="partnered_conflicts",
    )  # User B (опционально)
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    slug = models.SlugField(unique=True, blank=True)
    progress = models.FloatField(default=0.0)  # % прогресса
    resolved_at = models.DateTimeField(null=True, blank=True)
    deleted_by_creator = models.BooleanField(default=False)
    deleted_by_partner = models.BooleanField(default=False)

    truce_status = models.CharField(
        max_length=10, choices=TRUCE_STATUS_CHOICES, default="none"
    )

    # Кто был инициатором предложения
    truce_initiator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="initiated_truces",
    )
    
    # ИСПОЛЬЗОВАТЬ МЕТОДЫ ТОЛЬКО КАК ОРИЕНТИР ДЛЯ РЕАЛИЗАЦИИ НОВЫХ в Clean Arh

    # def save(self, *args, **kwargs):
    #     if not self.slug and not self.pk:  # Генерируем slug только при создании
    #         base_slug = slugify(
    #             f"{self.creator.username}-{uuid.uuid4()}"
    #         )  # Уникальный и безопасный
    #         self.slug = base_slug
    #     super().save(*args, **kwargs)

    # def add_partner(self, user):
    #     if self.partner:
    #         raise ValidationError("Партнер уже назначен.")
    #     if user == self.creator:
    #         raise ValidationError("Нельзя быть партнером самому себе.")
    #     self.partner = user
    #     self.status = "in_progress"
    #     # Здесь позже добавить уведомление (через notifications app), но пока игнорируем

    # def resolve(self, manual=False):
    #     # Логика завершения: manual=True позволяет завершить с progress < 100
    #     if manual or self.progress >= 100:
    #         self.status = "resolved"
    #         self.resolved_at = timezone.now()
    #     else:
    #         raise ValidationError(
    #             "Нельзя завершить без 100% прогресса, если не manually."
    #         )

    # def cancel(self):
    #     # Отклоненный конфликт
    #     if self.status in ("cancelled", "abandoned", "resolved"):
    #         raise ValidationError("Конфликт завершён, отменён или заброшен.")
    #     self.status = "cancelled"

    # def update_progress(self):
    #     items = self.items.all()  # type: ignore
    #     if items.exists():
    #         agreed_count = items.filter(is_agreed=True).count()
    #         self.progress = agreed_count / items.count() * 100
    #     else:
    #         self.progress = 0.0

    # def soft_delete_for_user(self, user):
    #     if user == self.creator:
    #         if self.deleted_by_creator:
    #             raise ValidationError("Конфликт уже удален")
    #         self.deleted_by_creator = True
    #     elif self.partner and user == self.partner:
    #         if self.deleted_by_partner:
    #             raise ValidationError("Конфликт уже удален")
    #         self.deleted_by_partner = True
    #     else:
    #         raise ValidationError("User не участник этого конфликта.")

    #     # Глобальное удаление, если оба удалили
    #     if self.deleted_by_creator and self.deleted_by_partner:
    #         self.delete()

    # def validate_truce_proposal(self, user):
    #     if user not in (self.creator, self.partner):
    #         return ValidationError("Вы не участник")

    #     if not (self.partner and self.creator):
    #         raise ValidationError("В конфликте не все участники.")

    #     if self.status != "in_progress":
    #         raise ValidationError(
    #             "Конфликт уже разрешен, отменен, заброшен или не начат."
    #         )

    #     if self.truce_status == "pending":
    #         return ValidationError("Предложение уже отправлено")

    #     is_answered = (
    #         not self.items.filter(creator_choice__isnull=True).exists()
    #         and not self.items.filter(partner_choice__isnull=True).exists()
    #     )

    #     if not is_answered:
    #         raise ValidationError("Не все пункты анкеты заполнены обоими участниками.")

    # @classmethod
    # def get_for_user(cls, user):
    #     return cls.objects.filter(
    #         is_deleted=False,
    #     ).filter(
    #         (models.Q(creator=user) & models.Q(deleted_by_creator=False))
    #         | (models.Q(partner=user) & models.Q(deleted_by_partner=False))
    #     )

    # def __str__(self):
    #     return f"Conflict {self.id} by {self.creator.username} ({self.status})"


class ConflictItemModel(IsDeletedModel):
    conflict = models.ForeignKey(
        ConflictModel, on_delete=models.CASCADE, related_name="items"
    )
    title = models.CharField(max_length=100)

    creator_choice_value = models.TextField(blank=True, null=True)
    partner_choice_value = models.TextField(blank=True, null=True)
    agreed_choice_value = models.TextField(blank=True, null=True)

    is_agreed = models.BooleanField(default=False)

    def __str__(self):
        return f"ConflictItemModel {self.id} for {self.conflict.id}"
    
    # ИСПОЛЬЗОВАТЬ МЕТОДЫ ТОЛЬКО КАК ОРИЕНТИР ДЛЯ РЕАЛИЗАЦИИ НОВЫХ в Clean Arh

    # def update_status(self):
    #     if self.creator_choice_value and self.partner_choice_value:
    #         # Если ответы совпадают - пункт согласован
    #         if self.creator_choice_value == self.partner_choice_value:
    #             self.is_agreed = True
    #             self.agreed_choice_value = self.creator_choice_value
    #         else:
    #             # Ответы есть, но они разные. Пункт не согласован.
    #             self.is_agreed = False
    #             self.agreed_choice_value = None
    #     else:
    #         # Если хотя бы один из пользователей еще не ответил, пункт не может быть согласован.
    #         self.is_agreed = False
    #         self.agreed_choice_value = None

    # def unlock(self):
    #     if self.conflict.status in ["resolved", "cancelled", "abandoned"]:
    #         raise ValidationError(
    #             "Нельзя изменить пункт в завершенном или отмененном конфликте."
    #         )

    #     if not self.is_agreed:
    #         # Еще не согласован, подстраховка, просто скип.
    #         return

    #     self.is_agreed = False
    #     self.agreed_choice_value = None


class ConflictEventModel(BaseModel):
    EVENT_META = {
        "truce_proposed": {
            "label": "Предложено перемирие",
            "requires": ["initiator"],
        },
        "truce_accepted": {
            "label": "Перемирие принято",
            "requires": ["initiator"],
        },
        "truce_declined": {
            "label": "Перемирие отклонено",
            "requires": ["initiator"],
        },
        "conflict_delete": {
            "label": "Конфликт удален",
            "requires": [],
        },
        "conflict_cancel": {
            "label": "Конфликт отменен",
            "requires": ["initiator"],
        },
        "item_agreed": {
            "label": "Пункт успешно согласован",
            "requires": ["initiator", "item"],
        },
        "item_add": {
            "label": "Пункт успешно добавлен",
            "requires": ["initiator"],
        },
        "conflict_join_success": {
            "label": "Пользователь успешно присоединился",
            "requires": ["initiator"],
        },
        "conflict_create": {
            "label": "Конфликт создан",
            "requires": ["initiator"],
        },
    }

    conflict = models.ForeignKey(
        ConflictModel, on_delete=models.CASCADE, related_name="events"
    )
    item = models.ForeignKey(
        ConflictItemModel, on_delete=models.CASCADE, related_name="items", null=True
    )

    # Кто инициировал событие
    initiator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    event_type = models.CharField(
        max_length=50,
        choices=[(key, meta["label"]) for key, meta in EVENT_META.items()],
    )

    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    
    # ИСПОЛЬЗОВАТЬ МЕТОДЫ ТОЛЬКО КАК ОРИЕНТИР ДЛЯ РЕАЛИЗАЦИИ НОВЫХ в Clean Arh

    # @staticmethod
    # async def acreate_event(conflict, event_type, **kwargs):
    #     """
    #     АСИНХРОННЫЙ универсальный метод для создания события.
    #     Предназначен для вызова из асинхронного кода.
    #     """
    #     meta = ConflictEventModel.EVENT_META.get(event_type)
    #     if not meta:
    #         raise ValueError(f"Неизвестный тип события: {event_type}")

    #     required = set(meta["requires"])
    #     missing = [r for r in required if r not in kwargs]
    #     if missing:
    #         raise ValueError(
    #             f"Для события '{event_type}' нужны аргументы: {', '.join(missing)}"
    #         )

    #     fields = dict(conflict=conflict, event_type=event_type)
    #     fields.update({key: kwargs.get(key) for key in ["initiator", "item"]})

    #     return await ConflictEventModel.objects.acreate(**fields)

    # def __str__(self):
    #     return (
    #         f"Событие '{self.get_event_type_display()}' в конфликте {self.conflict.id}"
    #     )
