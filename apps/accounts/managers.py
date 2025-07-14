from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from apps.common.managers import IsDeletedManager


class CustomUserManager(IsDeletedManager, BaseUserManager):
    def email_validator(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError("Вы должны указать действующий адрес электронной почты")

    def validate_superuser(self, **extra_fields):
        for field in ("is_staff", "is_superuser", "is_active"):
            extra_fields.setdefault(field, True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Суперпользователь должен иметь is_staff=True")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Суперпользователь должен иметь is_superuser=True")

        return extra_fields

    def create_user(self, email=None, **validated_data):
        if not email:
            raise ValidationError("Необходимо указать email")

        gender = validated_data.get("gender")
        if not gender:
            raise ValidationError("Необходимо указать пол")

        password1 = validated_data.pop("password1", None)
        if not password1:
            raise ValidationError("Пароль обязателен")

        self.email_validator(email)
        email = self.normalize_email(email)

        user = self.model(email=email, **validated_data)
        user.set_password(password1)

        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, **validated_data):
        validated_data.setdefault("is_superuser", True)
        validated_data.setdefault('is_staff', True)

        password = validated_data.pop('password', None)
        if not password:
            raise ValidationError("Пароль обязателен для суперпользователя")

        validated_data['password1'] = password
        return self.create_user(email=email, **validated_data)
