from rest_framework import serializers
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    password2 = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError("Пароли не совпадают")
        return attrs

    def validate_email(self, email):
        # Формат email
        email = email.strip().lower()
        try:
            validate_email(email)  # Django validator
        except ValidationError:
            raise serializers.ValidationError("Укажите действительный email")
        return email

    def validate_username(self, username):
        # Формат username
        username = username.strip()
        if len(username) < 3:
            raise serializers.ValidationError("Не менее 3 символов")
        if not re.match(r"^[a-zA-Z0-9._-]+$", username):
            raise serializers.ValidationError(
                "Только буквы, цифры, точка, дефис и подчёркивание"
            )
        if re.match(r"^\d+$", username):
            raise serializers.ValidationError(
                "Нельзя использовать только цифры в имени"
            )
        return username


class LoginSerializer(serializers.Serializer):
    login = serializers.CharField() 
    password = serializers.CharField(style={"input_type": "password"})
    
    def validate_login(self, value):
        """Нормализуем логин"""
        return value.strip().lower()  # убираем пробелы, в нижний регистр
