from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from apps.common.models import IsDeletedModel
from django.db.models.functions import Lower


class UserModel(AbstractBaseUser, IsDeletedModel, PermissionsMixin):
    username = models.CharField("Login", max_length=30, unique=True)
    email = models.EmailField("Email address", unique=True)
    email_confirmed = models.BooleanField("Email подтвержден", default=False)
    is_staff = models.BooleanField("staff status", default=False)
    is_superuser = models.BooleanField("superuser status", default=False)
    is_god = models.BooleanField("Создатель системы", default=False)
    is_active = models.BooleanField("active", default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        swappable = "AUTH_USER_MODEL"
        ordering = ["-created_at"]

        indexes = [
            models.Index(Lower("email"), name="user_email_ci_idx"),
            models.Index(Lower("username"), name="user_username_ci_idx"),
        ]

