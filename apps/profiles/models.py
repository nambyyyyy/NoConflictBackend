from django.db import models
from django.contrib.auth import get_user_model
from apps.common.models import BaseModel

User = get_user_model()


class ProfileModel(BaseModel):
    class Gender(models.TextChoices):
        MALE = "M", "Мужской"
        FEMALE = "F", "Женский"

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile", verbose_name="users"
    )
    first_name = models.CharField(verbose_name="Имя", max_length=50, blank=True)
    last_name = models.CharField(verbose_name="Фамилия", max_length=50, blank=True)
    gender = models.CharField(
        verbose_name="Пол", max_length=1, choices=Gender.choices, blank=True, null=True
    )
    avatar_filename = models.ImageField(
        verbose_name="Аватар",
        upload_to="avatars/%Y/%m/%d/",
        blank=True,
        default="avatars/default.jpg",
    )

    location = models.CharField("Местоположение", max_length=30, blank=True)
    bio = models.TextField("О себе", blank=True)
