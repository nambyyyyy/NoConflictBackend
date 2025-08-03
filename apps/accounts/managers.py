from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import validate_email
from django.core.exceptions import ValidationError, PermissionDenied
from apps.common.managers import IsDeletedManager


class CustomUserManager(IsDeletedManager, BaseUserManager):
    def email_validator(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError("Вы должны указать действующий адрес электронной почты")

    def create_user(self, email, password, **validated_data):
        if password is None:
            raise ValueError("Password cannot be None")
        if email is None:
            raise ValueError("Email cannot be None")

        self.email_validator(email)
        email = self.normalize_email(email)

        user = self.model(email=email, password=password, **validated_data)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **extra_fields):      
        if extra_fields.get('is_staff') is False:
            raise ValueError("Суперпользователь должен иметь is_staff=True")
        if extra_fields.get('is_superuser') is False:
            raise ValueError("Суперпользователь должен иметь is_superuser=True")
        
        request = extra_fields.pop("request", None)
        
        if request and not request.user.is_god:
            raise PermissionDenied(
                "Только создатель системы может назначать суперпользователей"
            )
                
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)

    def create_staffuser(self, email, password, **extra_fields):
        if extra_fields.get('is_staff') is False:
            raise ValueError("Staffuser must have is_staff=True")
    
        request = extra_fields.pop('request', None)
        
        if request and not (request.user.is_superuser or request.user.is_god):
            raise PermissionDenied("Только админы могут создавать персонал")
        
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)

        return self.create_user(email, password, **extra_fields)
