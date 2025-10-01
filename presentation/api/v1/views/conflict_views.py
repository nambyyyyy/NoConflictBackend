from rest_framework.views import APIView
from rest_framework.response import Response
from presentation.api.v1.serializers.conflict_serializers import (
    CreateConflictSerializer,
)
from presentation.dependencies.service_factories import get_conflict_service
from application.dtos.conflict_dto import ConflictDetailDTO
from application.services.conflict_service import ConflictService
from typing import Any, Dict
from rest_framework.permissions import IsAuthenticated


class CreateConflictView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        conflict_service: ConflictService = get_conflict_service()
        empty_conflict_dto: ConflictDetailDTO = conflict_service.get_form_conflict(
            request.user.id
        )
        return Response(empty_conflict_dto.__dict__, status=200)

    def post(self, request):
        serializer = CreateConflictSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Получаем данные как чистый dict
        data: Dict[str, Any] = serializer.validated_data  # type: ignore

        # Получаем сервис (Application Layer)
        conflict_service: ConflictService = get_conflict_service()

        try:
            conflict_dto: ConflictDetailDTO = conflict_service.create_conflict(
                request.user.id, data
            )
            return Response(conflict_dto.__dict__, status=201)

        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": "Internal server error"}, status=500)
