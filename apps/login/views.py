from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer, MyTokenObtainPairSerializer
from apps.common.permissions import IsUnauthenticated


class LoginView(APIView):
    permission_classes = [IsUnauthenticated]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            user.last_login = timezone.now()
            user.save(update_fields=["last_login"])

            refresh = MyTokenObtainPairSerializer.get_token(user)
            access = refresh.access_token

            return Response(
                {
                    "message": "Успешный вход",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "group": (
                            "creator" if getattr(user, "is_god", False) else
                            "admin" if user.is_superuser else
                            "moderator" if user.is_staff else
                            "user"
                        )
                    },
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(access),
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
