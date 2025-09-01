from rest_framework.views import APIView
from rest_framework.response import Response
from application.services import AuthService
from presentation.api.v1.serializers import RegisterSerializer, LoginSerializer
from apps.common.permissions import IsUnauthenticated
from presentation.dependencies.service_factories import get_auth_service
from apps.accounts.tasks import send_verification_email
from application.services import AuthService


class RegisterView(APIView):
    permission_classes = [IsUnauthenticated]

    def post(self, request):
        try:
            # 1. Валидация входных данных
            serializer = RegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # 2. Создаем сервис и репозиторий
            auth_service: AuthService = get_auth_service()
            base_url = request.build_absolute_uri("/")[:-1]

            # 3. Вызываем use case
            user_dto = auth_service.register_user(
                email=serializer.validated_data["email"],  # type: ignore
                username=serializer.validated_data["username"],  # type: ignore
                password=serializer.validated_data["password"],  # type: ignore
                send_email_func=send_verification_email.delay,  # type: ignore
                base_url=base_url,
            )

            return Response(user_dto.__dict__, status=201)

        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": "Internal server error"}, status=500)


class VerifyEmailView(APIView):
    permission_classes = [IsUnauthenticated]

    def get(self, request, uidb64, token):
        try:
            auth_service: AuthService = get_auth_service()
            user_dto = auth_service.verify_email(uidb64=uidb64, token=token)

            return Response(user_dto.__dict__, status=200)

        except (TypeError, ValueError, OverflowError, UnicodeDecodeError) as e:
            return Response({"error": str(e)}, status=400)


class LoginView(APIView):
    permission_classes = [IsUnauthenticated]

    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            auth_service: AuthService = get_auth_service()

            tokens: dict[str, str] = auth_service.login(
                login=serializer.validated_data["login"],  # type: ignore
                password=serializer.validated_data["password"],  # type: ignore
            )

            return Response(tokens, status=200)

        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": "Internal server error"}, status=500)
