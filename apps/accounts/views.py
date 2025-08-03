from apps.accounts.serializers import RegisterUserSerializer 
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from apps.accounts.serializers import MyTokenObtainPairSerializer
from rest_framework.permissions import AllowAny
from rest_framework import generics
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer
    
    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        is_superuser = validated_data.pop('is_superuser', False)
        
        if is_superuser:
            user = User.objects.create_superuser(**validated_data)
            return user
        
        is_staff = validated_data.pop('is_staff', False)
        
        if is_staff:
            user = User.objects.create_staffuser(**validated_data)          
        else:
            user = User.objects.create_user(**validated_data)
        
        return user

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer