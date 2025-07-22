from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.exceptions import ValidationError
import uuid
from apps.common.models import IsDeletedModel, BaseModel
from django.utils import timezone
User = get_user_model()  # Получаем вашу модель User (из accounts или auth)


class Conflict(IsDeletedModel):
    STATUS_CHOICES = [
        ("pending", "Ожидает партнера"),  # Когда создан без партнёра
        ("in_progress", "В процессе"),  # Когда оба пользователя присоединены
        ("resolved", "Разрешен"),  # Полностью согласован или manually завершён
        ("cancelled", "Отменен"),  # Отказ от продолжения
        ("abandoned", "Заброшен")  # Заброшен. Вызывается отдельно скриптом в случае истечения срока действия.
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
    title = models.CharField(max_length=255, blank=True)  # Опциональный заголовок
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    slug = models.SlugField(unique=True, blank=True)
    progress = models.FloatField(default=0.0)  # % прогресса
    resolved_at = models.DateTimeField(null=True, blank=True)
    deleted_by_creator = models.BooleanField(default=False)
    deleted_by_partner = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        if not self.slug and not self.pk:  # Генерируем slug только при создании
            base_slug = slugify(
                f"{self.creator.username}-{uuid.uuid4()}"
            )  # Уникальный и безопасный
            self.slug = base_slug
        super().save(*args, **kwargs)

    def add_partner(self, user):
        if self.partner:
            raise ValidationError("Партнер уже назначен.")
        if user == self.creator:
            raise ValidationError("Нельзя быть партнером самому себе.")
        self.partner = user
        self.status = "in_progress"
        self.save()
        # Здесь позже можно добавить уведомление (через notifications app), но пока игнорируем

    def resolve(self, manual=False):
        # Логика завершения: manual=True позволяет завершить с progress < 100
        if manual or self.progress >= 100:
            self.status = "resolved"
            self.resolved_at = timezone.now()
            self.save()
        else:
            raise ValidationError(
                "Нельзя завершить без 100% прогресса, если не manually."
            )

    def cancel(self):
        # Отклоненный конфликт
        if self.status in ("cancelled", "abandoned", "resolved"):
            raise ValidationError("Конфликт завершён, отменён или заброшен.")
        self.status = "cancelled"
        self.save()

    def update_progress(self):
        items = self.items.all() # type: ignore
        if items.exists():
            agreed_count = items.filter(is_agreed=True).count()
            self.progress = agreed_count / items.count() * 100
        else:
            self.progress = 0.0


    def soft_delete_for_user(self, user):
        if user == self.creator:
            if self.deleted_by_creator:
                raise ValidationError("Конфликт уже удален")
            self.deleted_by_creator = True
        elif self.partner and user == self.partner:
            if self.deleted_by_partner:
                raise ValidationError("Конфликт уже удален")
            self.deleted_by_partner = True
        else:
            raise ValidationError("User не участник этого конфликта.")

        # Глобальное удаление, если оба удалили
        if self.deleted_by_creator and self.deleted_by_partner:
            self.delete()

        self.save()

    @classmethod
    def get_for_user(cls, user):
        return cls.objects.filter(
            is_deleted=False,
        ).filter(
            (models.Q(creator=user) & models.Q(deleted_by_creator=False)) |
            (models.Q(partner=user) & models.Q(deleted_by_partner=False))
        )


    def __str__(self):
        return f"Conflict {self.id} by {self.creator.username} ({self.status})"


class ConflictItem(BaseModel):
    ITEM_TYPES = [
        ("reason", "Причина конфликта"),
        ("description", "Описание ситуации"),
        ("impact", "Влияние на стороны"),
        ("proposal", "Предложение решения"),
    ]

    conflict = models.ForeignKey(
        Conflict, on_delete=models.CASCADE, related_name="items"
    )
    item_type = models.CharField(max_length=100, choices=ITEM_TYPES)

    available_options = models.ManyToManyField(
        "OptionChoice",
        related_name="used_in_items"
    )

    # 2. Выбор создателя и партнера теперь ссылается на OptionChoice.
    creator_choice = models.ForeignKey(
        "OptionChoice",
        on_delete=models.SET_NULL,
        related_name="chosen_by_creators",
        null=True, blank=True
    )
    partner_choice = models.ForeignKey(
        "OptionChoice",
        on_delete=models.SET_NULL,
        related_name="chosen_by_partners",
        null=True, blank=True
    )
    agreed_choice = models.ForeignKey(
        "OptionChoice",
        on_delete=models.SET_NULL,
        related_name="agreed_in_conflicts",
        null=True, blank=True
    )

    is_agreed = models.BooleanField(default=False)

    def __str__(self):
        return f"ConflictItem {self.id} for {self.conflict.id}"

    def update_status(self):
        if self.creator_choice and self.partner_choice:
            # Если ответы совпадают - пункт согласован!
            if self.creator_choice == self.partner_choice:
                self.is_agreed = True
                self.agreed_choice = self.creator_choice
            else:
                # Ответы есть, но они разные. Пункт не согласован.
                self.is_agreed = False
                self.agreed_choice = None
        else:
            # Если хотя бы один из пользователей еще не ответил, пункт не может быть согласован.
            self.is_agreed = False
            self.agreed_choice = None


    def unlock(self):
        if self.conflict.status in ['resolved', 'cancelled', 'abandoned']:
            raise ValidationError("Нельзя изменить пункт в завершенном или отмененном конфликте.")

        if not self.is_agreed:
            # Еще не согласован, подстраховка, просто скип.
            return

        self.is_agreed = False
        self.agreed_choice = None


class OptionChoice(BaseModel):
    value = models.TextField(unique=True) # Текст варианта. Должен быть уникальным.
    is_predefined = models.BooleanField(default=False) # Флаг, что это наш "шаблон"

    def __str__(self):
        return self.value
