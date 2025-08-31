from rest_framework import serializers
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import AuthenticationFailed

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    login = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        login = attrs.get("login", "").strip().lower()
        password = attrs.get("password")

        if not login:
            raise serializers.ValidationError(
                {"login": "Это поле обязательно для заполнения."}
            )
        if not password:
            raise serializers.ValidationError(
                {"password": "Это поле обязательно для заполнения."}
            )
        
        user = User.objects.filter(
            Q(username__iexact=login) | Q(email__iexact=login)
        ).first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError("Неверные учетные данные")

        if not user.is_active:
            raise serializers.ValidationError("Пользователь заблокирован")

        if not getattr(user, "email_confirmed", False):
            raise serializers.ValidationError("Email не подтверждён")

        attrs["user"] = user
        return attrs

    
    


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Добавляем пользовательские данные в полезную нагрузку
        if user.is_god:
            token["group"] = "creator"
        elif user.is_superuser:
            token["group"] = "admin"
        elif user.is_staff:
            token["group"] = "moderator"
        else:
            token["group"] = "user"

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        if not getattr(self.user, "email_confirmed", False):
            # Не выдаём токены, пока почта не подтверждена
            raise AuthenticationFailed(
                "E-mail не подтверждён.", code="email_not_confirmed"
            )
        return data
