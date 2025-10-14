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
from django.db import transaction


class ConflictView(APIView):
    permission_classes = [IsAuthenticated]

    async def get(self, request, slug):
        conflict_service: ConflictService = get_conflict_service()

        try:
            conflict_dto: ConflictDetailDTO = await conflict_service.get_conflict(
                request.user.id, slug
            )
            response_data = conflict_dto.__dict__
            response_data["ws_url"] = f"/ws/conflicts/{slug}/"
            return Response(response_data, status=200)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": "Internal server error"}, status=500)


class CreateConflictView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateConflictSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Получаем данные как чистый dict
        validated_data: Dict[str, Any] = serializer.validated_data  # type: ignore

        # Получаем сервис (Application Layer)
        conflict_service: ConflictService = get_conflict_service()
        creator_id = request.user.id
        partner_id = validated_data.pop("partner_id", None)
        title = validated_data.pop("title", None)
        items = validated_data.pop("items", None)

        try:
            conflict_dto: ConflictDetailDTO = conflict_service.create_conflict(
                creator_id, partner_id, title, items, transaction.atomic
            )
            return Response(conflict_dto.__dict__, status=201)

        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": "Internal server error"}, status=500)
