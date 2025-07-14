from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class CreateUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    gender = serializers.ChoiceField(
        choices=User.Gender.choices,
        required=True,
        error_messages={
            'required': 'Пол обязателен для заполнения',
            'invalid_choice': 'Укажите правильный вариант пола'
        }
    )

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "first_name",
            "last_name",
            "gender",
            "avatar",
            "password1",
            "password2",
        ]

    def validate(self, data):
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError({"password2": "Пароли не совпадают"})

        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError(
                {"email": "Пользователь с таким email уже существует"}
            )

        return data


    def create(self, validated_data):
        validated_data.pop("password2", None)
        return User.objects.create_user(**validated_data)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Добавляем пользовательские данные в полезную нагрузку
        if user.is_staff:
            token['group'] = 'admin'
        else:
            token['group'] = 'user'

        return token