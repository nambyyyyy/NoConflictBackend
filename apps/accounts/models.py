from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from apps.common.models import IsDeletedModel
from apps.accounts.managers import CustomUserManager


class User(AbstractBaseUser, IsDeletedModel, PermissionsMixin):
    objects = CustomUserManager()

    class Gender(models.TextChoices):
        MALE = "M", "Мужской"
        FEMALE = "F", "Женский"

    email = models.EmailField(
        verbose_name="Email address",
        unique=True,
        blank=False,
        error_messages={
            "unique": "Пользователь с таким email уже существует",
            "required": "Обязательное поле",
        },
    )
    username = models.CharField(
        verbose_name="Логин", max_length=30, blank=False, unique=True
    )
    first_name = models.CharField(verbose_name="Имя", max_length=150, blank=True)
    last_name = models.CharField(verbose_name="Фамилия", max_length=150, blank=True)
    gender = models.CharField(
        verbose_name="Пол",
        max_length=1,
        choices=Gender.choices,
        blank=False,
        default=None,
    )
    avatar = models.ImageField(
        verbose_name="Аватар",
        upload_to="avatars/",
        blank=True,
        null=True,
        default="avatars/default.jpg",
    )
    email_confirmed = models.BooleanField(
        verbose_name="Email подтвержден", default=False
    )
    is_staff = models.BooleanField(
        verbose_name="staff status",
        default=False,
    )
    is_superuser = models.BooleanField(
        verbose_name="superuser status",
        default=False,
    )
    is_god = models.BooleanField(
        default=False,
        verbose_name="Создатель системы",
        help_text="Абсолютные права"
    )
    is_active = models.BooleanField(
        verbose_name="active",
        default=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "gender"]

    def __str__(self):
        return self.username or f"Email: {self.email}"

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip() or self.username or self.email

    def get_short_name(self):
        return self.first_name or self.username

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        swappable = "AUTH_USER_MODEL"
        ordering = ["-created_at"]
