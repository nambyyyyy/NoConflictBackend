from django.db import models
from django.contrib.auth import get_user_model
from apps.common.models import BaseModel

User = get_user_model()


class Profile(BaseModel):
    class Gender(models.TextChoices):
        MALE = "M", "Мужской"
        FEMALE = "F", "Женский"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    gender = models.CharField(
        max_length=1, choices=Gender.choices, blank=True, null=True
    )
    avatar = models.ImageField(
        verbose_name="Аватар",
        upload_to="avatars/",
        blank=True,
        null=True,
        default="avatars/default.jpg",
    )

    location = models.CharField(max_length=30, blank=True)
    bio = models.TextField(blank=True)
