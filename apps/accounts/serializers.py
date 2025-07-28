from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, 
                                     required=True,
                                     style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, 
                                      required=True, 
                                      style={'input_type': 'password'}, 
                                      label="Confirm password")


    email = serializers.EmailField(required=True)
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
            "gender",
            "first_name",
            "last_name", 
            "avatar",
            "password",
            "password2",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Пароли не совпадают"})

        return attrs


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
    

class RegisterUserSerializer(CreateUserSerializer):
    # Наследуемся от CreateUserSerializer, чтобы не дублировать код
    tokens = serializers.SerializerMethodField(read_only=True)

    class Meta(CreateUserSerializer.Meta):
        # Добавляем поле tokens к полям родителя
        fields = CreateUserSerializer.Meta.fields + ['tokens']

    def get_tokens(self, user):
        # Используем MyTokenObtainPairSerializer для генерации токенов
        # Это гарантирует, что кастомные claims (например, 'group') тоже будут добавлены
        refresh = MyTokenObtainPairSerializer.get_token(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }