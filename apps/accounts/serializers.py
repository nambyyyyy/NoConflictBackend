from rest_framework import serializers
from django.contrib.auth import get_user_model
import re
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    password2 = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "password",
            "password2",
        )
        extra_kwargs = {
            "username": {"max_length": 30, "required": True},
            "email": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Пароли не совпадают"})

        tmp_user = User(
            email=attrs.get("email", ""), username=attrs.get("username", "")
        )
        try:
            validate_password(attrs["password"], user=tmp_user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return attrs

    def validate_email(self, email):
        v = email.strip().lower()
        if User.objects.filter(email__iexact=v).exists():
            raise serializers.ValidationError("Этот email уже используется")
        try:
            validate_email(v)
        except ValidationError:
            raise serializers.ValidationError("Вы должны указать действующий адрес электронной почты")
            
        return v

    def validate_username(self, username):
        v = username.strip()
        if len(v) < 3:
            raise serializers.ValidationError(
                "Имя пользователя должно быть не менее 3 символов"
            )
        if not re.match(r"^[A-Za-z0-9._-]+$", v):
            raise serializers.ValidationError(
                "Имя может содержать буквы, цифры, точку, дефис и подчёркивание"
            )
        if re.match(r"^\d+$", v):
            raise serializers.ValidationError(
                "Нельзя использовать только цифры в имени"
            )
        if User.objects.filter(username__iexact=v).exists():
            raise serializers.ValidationError("Этот username уже используется")
        
        return v

    def create(self, validated_data):
        password = validated_data.pop("password")
        email = validated_data.pop("email")
        validated_data.pop("password2", None)
        user = User.objects.create_user(
            email=email, password=password, **validated_data
        )
        return user
