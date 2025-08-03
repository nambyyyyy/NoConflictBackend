from django.db import models
from django.contrib.auth import get_user_model
from apps.common.models import IsDeletedModel

User = get_user_model()


class Partner(IsDeletedModel):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="partners", verbose_name="Владелец"
    )
    partner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="partnered_with",
        verbose_name="Партнер",
    )

    def __str__(self):
        return self.partner.username

    class Meta:
        unique_together = ("owner", "partner")
        verbose_name = "Партнер"
        verbose_name_plural = "Партнеры"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
        ]

    def save(self, *args, **kwargs):
        if self.owner == self.partner:
            raise ValueError("Нельзя добавить самого себя в партнеры.")
        super().save(*args, **kwargs)



class PartnerRequest(IsDeletedModel):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_requests"
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_requests"
    )

    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)

    class Meta:
        unique_together = ("sender", "receiver")
        verbose_name = "Запрос на партнёрство"
        verbose_name_plural = "Запросы на партнёрство"

    def __str__(self):
        return f"{self.sender} → {self.receiver}"

    def save(self, *args, **kwargs):
        if self.sender == self.receiver:
            raise ValueError("Нельзя отправить запрос самому себе.")
        if self.is_accepted and self.is_rejected:
            raise ValueError("Запрос не может быть одновременно принят и отклонён.")
        super().save(*args, **kwargs)
