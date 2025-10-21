from rest_framework.views import APIView
from rest_framework.response import Response
from presentation.api.v1.serializers.conflict_serializers import (
    CreateConflictSerializer,
)
from presentation.dependencies.service_factories import get_conflict_service
from application.services.conflict_service import ConflictService
from typing import Any, Dict
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from channels.layers import get_channel_layer


class ConflictView(APIView):
    permission_classes = [IsAuthenticated]

    async def get(self, request, slug):
        conflict_service: ConflictService = get_conflict_service()

        try:
            conflict_dto: dict[str, Any] = await conflict_service.get_conflict(
                request.user.id, slug
            )
            conflict_dto["ws_url"] = f"/ws/conflicts/{slug}/"
            return Response(conflict_dto, status=200)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": "Internal server error"}, status=500)


class CreateConflictView(APIView):
    permission_classes = [IsAuthenticated]

    async def post(self, request):
        serializer = CreateConflictSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Получаем данные как чистый dict
        validated_data: Dict[str, Any] = serializer.validated_data  # type: ignore

        # Получаем сервис (Application Layer)
        conflict_service: ConflictService = get_conflict_service()
        
        try:
            conflict_dto: dict[str, Any] = await conflict_service.create_conflict(
                request.user.id,
                validated_data.pop("partner_id", None),
                validated_data.pop("title", None),
                validated_data.pop("items", None),
                transaction.atomic,
            )
            return Response(conflict_dto.__dict__, status=201)

        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": "Internal server error"}, status=500)


class CancelConflictView(APIView):
    permission_classes = [IsAuthenticated]

    async def post(self, request, slug):
        conflict_service: ConflictService = get_conflict_service()

        try:
            conflict_dto: dict[str, Any] = await conflict_service.cancel_conflict(
                request.user.id, slug, transaction.atomic, get_channel_layer
            )
            conflict_dto["ws_url"] = f"/ws/conflicts/{slug}/"
            return Response(conflict_dto, status=201)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": "Internal server error"}, status=500)


class CreateOfferTruceView(APIView):
    permission_classes = [IsAuthenticated]
    
    async def post(self, request, slug):
        conflict_service: ConflictService = get_conflict_service()
        
        try:

            conflict_dto: dict[str, Any] = await conflict_service.create_offer_truce(
                request.user.id, slug, transaction.atomic, get_channel_layer
            )
            conflict_dto["ws_url"] = f"/ws/conflicts/{slug}/"
            return Response(conflict_dto, status=201)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": "Internal server error"}, status=500)


class CancelOfferTruce(APIView):
    permission_classes = [IsAuthenticated]
    
    async def post(self, request, slug):
        conflict_service: ConflictService = get_conflict_service()
        
        try:
            conflict_dto: dict[str, Any] = await conflict_service.cancel_offer_truce(
                request.user.id, slug, transaction.atomic, get_channel_layer
            )
            conflict_dto["ws_url"] = f"/ws/conflicts/{slug}/"
            return Response(conflict_dto, status=201)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": "Internal server error"}, status=500)