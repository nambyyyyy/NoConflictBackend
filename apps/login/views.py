from rest_framework.views import APIView
from rest_framework.response import Response
from apps.login.serializers import LoginSerializer
from rest_framework import status
from django.utils import timezone
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken


class IsUnauthenticated(permissions.BasePermission):
    """
    Разрешает доступ только неавторизованным пользователям.
    """

    def has_permission(self, request, view):
        return not request.user.is_authenticated


class LoginView(APIView):
    permission_classes = [IsUnauthenticated]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            user.last_login = timezone.now()
            user.save()

            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "message": "Успешный вход",
                    "user": {"email": user.email, "id": user.id},
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
