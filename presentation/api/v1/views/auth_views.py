from rest_framework.views import APIView
from rest_framework.response import Response
from application.services import AuthService
from infrastructure.persistence.user_repository import DjangoUserRepository
from presentation.api.v1.serializers import RegisterSerializer
from apps.common.permissions import IsUnauthenticated


class RegisterView(APIView):
    permission_classes = [IsUnauthenticated]
    
    def post(self, request):
        try:
            # 1. Валидация входных данных
            serializer = RegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # 2. Создаем сервис и репозиторий
            user_repo = DjangoUserRepository()
            auth_service = AuthService(user_repository=user_repo)
            
            # 3. Вызываем use case
            user_dto = auth_service.register_user(
                email=request.data['email'],
                username=request.data['username'],
                password=request.data['password']
            )
            
            return Response(user_dto.__dict__, status=201)
            
        except ValueError as e:
            return Response({'error': str(e)}, status=400)