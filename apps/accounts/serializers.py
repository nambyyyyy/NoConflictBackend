from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import re
from django.core.exceptions import PermissionDenied

User = get_user_model()


class CreateUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        error_messages={
            "required": "Обязательное поле",
            "max_length": "Логин не должен превышать 50 символов",
            "blank": "Логин не может быть пустым",
        },
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={"required": "Обязательное поле"},
        style={"input_type": "password"},
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={"required": "Обязательное поле"},
        style={"input_type": "password"},
        label="Confirm password",
    )

    email = serializers.EmailField(
        required=True, error_messages={"required": "Обязательное поле"}
    )
    gender = serializers.ChoiceField(
        choices=User.Gender.choices,  # type: ignore
        required=True,
        error_messages={
            "required": "Обязательное поле",
            "invalid_choice": "Укажите правильный вариант пола",
        },
    )

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "gender",
            "first_name",
            "last_name",
            "avatar",
            "password",
            "password2",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "is_staff": {"read_only": True},
            "is_superuser": {"read_only": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Пароли не совпадают"})

        if len(attrs["password"]) < 8:
            raise serializers.ValidationError(
                {"password": "Пароль должен быть не менее 8 символов"}
            )

        request = self.context.get("request")

        if attrs.get("is_superuser"):
            if not (request and request.user.is_god):
                raise PermissionDenied(
                    "Только создатель системы может назначать суперпользователей"
                )
        
        if attrs.get('is_staff'):
            if not (request and (request.user.is_superuser or request.user.is_god)):
                raise PermissionDenied("Только админы или создатель могут создавать персонал")

        attrs.pop("password2")
        return attrs

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value.lower().strip()).exists():
            raise serializers.ValidationError("Этот email уже используется")
        return value

    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError(
                "Имя пользователя должно быть не менее 3 символов"
            )

        if value in ("admin", "root", "support", "system", "nambyyyyy"):
            raise serializers.ValidationError("Это имя запрещено сервисом")
        if not re.match(r"^[\w.@+-]{3,30}$", value):
            raise serializers.ValidationError("Допустимы буквы, цифры и @/./+/-/_")
        if re.match(r"^\d+$", value):
            raise serializers.ValidationError("Нельзя только цифры")

        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Этот username уже используется")

        return value


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Добавляем пользовательские данные в полезную нагрузку
        if user.is_staff:
            token["group"] = "admin"
        else:
            token["group"] = "user"

        return token


class RegisterUserSerializer(CreateUserSerializer):
    # Наследуемся от CreateUserSerializer, чтобы не дублировать код
    tokens = serializers.SerializerMethodField(read_only=True)

    class Meta(CreateUserSerializer.Meta):
        # Добавляем поле tokens к полям родителя
        fields = CreateUserSerializer.Meta.fields + ["tokens"]

    def get_tokens(self, user):
        # Используем MyTokenObtainPairSerializer для генерации токенов
        # Это гарантирует, что кастомные claims (например, 'group') тоже будут добавлены
        refresh = MyTokenObtainPairSerializer.get_token(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
