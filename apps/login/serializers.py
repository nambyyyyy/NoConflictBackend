from rest_framework import serializers
from django.contrib.auth import authenticate


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if not email:
            raise serializers.ValidationError(
                {"email": "Это поле обязательно для заполнения."}
            )

        if not password:
            raise serializers.ValidationError(
                {"password": "Это поле обязательно для заполнения."}
            )

        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError("Неверные учетные данные")

        if not user.is_active:
            raise serializers.ValidationError("Пользователь заблокирован")

        if not user.email_confirmed:
            raise serializers.ValidationError("Email не подтверждён")

        return {'user': user}
