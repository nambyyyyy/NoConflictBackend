from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.exceptions import ValidationError
import uuid
from apps.common.models import IsDeletedModel, BaseModel
from time import timezone

User = get_user_model()  # Получаем вашу модель User (из accounts или auth)


class Conflict(IsDeletedModel):
    STATUS_CHOICES = [
        ("pending", "Ожидает партнера"),  # Когда создан без партнёра
        ("in_progress", "В процессе"),  # Когда оба пользователя присоединены
        ("resolved", "Разрешен"),  # Полностью согласован или manually завершён
        ("сancelled", "Отменен"),  # Отказ от продолжения
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
        if manual or self.progress == 100:
            self.status = "resolved"
            self.resolved_at = timezone.now()
            self.save()
        else:
            raise ValidationError(
                "Нельзя завершить без 100% прогресса, если не manually."
            )

    def abandon(self):
        # Отклоненный конфликт
        self.status = "abandoned"
        self.save()

    def update_progress(self):
        items = self.items.all()
        if items.exists():
            agreed_count = items.filter(is_agreed=True).count()
            self.progress = agreed_count / items.count() * 100
        else:
            self.progress = 0.0
        self.save(update_fields=["progress"])

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
    value_creator = models.TextField(blank=True)  # Версия User A
    value_partner = models.TextField(blank=True)  # Версия User B
    agreed_value = models.TextField(
        blank=True
    )  # Согласованная версия (копируется при подтверждении)
    is_agreed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ConflictItem {self.id} for {self.conflict.id}"

    class Meta:
        unique_together = ("conflict", "item_type")  # Один пункт на тип per conflict

    def confirm_by(self, user, value_to_confirm):
        if user == self.conflict.creator:
            self.agreed_value = value_to_confirm  # Подтверждает версию B
        elif user == self.conflict.partner:
            self.agreed_value = value_to_confirm  # Подтверждает версию A
        else:
            raise ValidationError("Только участники могут подтверждать.")
        self.is_agreed = True
        self.save()
        self.conflict.update_progress()  # Обновить прогресс


class OptionItem(BaseModel):
    conflict_item = models.ForeignKey(ConflictItem, on_delete=models.CASCADE, related_name="point")
    value_option = models.CharField(related_name="option")

    class Meta:
        unique_together = ("conflict_item", "value_option")
    
    def __str__(self):
        return f"OptionItem {self.value_option} for {self.conflict_item}"


