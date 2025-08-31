from apps.accounts.serializers import RegisterSerializer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse
from apps.common.permissions import IsUnauthenticated
from django.db import transaction
from apps.accounts.tasks import send_verification_email

User = get_user_model()


class RegisterAPIView(APIView):
    permission_classes = [IsUnauthenticated]

    def post(self, request):
        s = RegisterSerializer(data=request.data, context={"request": request})
        s.is_valid(raise_exception=True)
        user = s.save()

        base_url = request.build_absolute_uri("/")[:-1]
        
        transaction.on_commit(
            lambda: send_verification_email.delay(user.id, base_url)
        )

        return Response(
            {
                "detail": "Вы успешно зарегистрированы. Проверьте почту и подтвердите e-mail. "
                          "Если письма нет — проверьте спам.",
                "email": user.email,
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailAPIView(APIView):
    permission_classes = [IsUnauthenticated]

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.filter(pk=uid).first()
        except (TypeError, ValueError, OverflowError, UnicodeDecodeError):
            user = None

        # Проверка пользователя
        if not user:
            return Response(
                {"detail": "Неверная ссылка."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка на удаление 
        if hasattr(user, 'is_deleted') and user.is_deleted:
            return Response(
                {"detail": "Аккаунт был удален."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка токена
        if not default_token_generator.check_token(user, token):
            return Response(
                {"detail": "Ссылка недействительна или устарела."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Проверка уже подтвержденного email
        if user.email_confirmed:
            return Response(
                {"detail": "E-mail уже подтверждён."}, 
                status=status.HTTP_200_OK
            )

        # Подтверждение email
        user.email_confirmed = True  
        user.save(update_fields=["email_confirmed"])

        return Response(
            {
                "detail": "E-mail успешно подтверждён.", 
                "email": user.email
            },
            status=status.HTTP_200_OK,
        )
        
        
        
        
