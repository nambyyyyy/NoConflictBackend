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
from typing import Optional


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


class BaseConflictActionView(APIView):
    permission_classes = [IsAuthenticated]
    service_method_name: Optional[str] = None

    async def _action(self, request, slug: Optional[str], method: str):
        conflict_service: ConflictService = get_conflict_service()
        if not self.service_method_name:
            raise NotImplementedError("service_method_name must be defined")

        service_method = getattr(conflict_service, self.service_method_name)

        if method == "get":
            result = await service_method(request.user.id, slug)
        elif method == "post":
            result = await service_method(
                request.user.id, slug, transaction.atomic, get_channel_layer
            )
        elif method == "delete":
            await service_method(request.user.id, slug, transaction.atomic)
            return
        else:
            raise ValueError(f"Unsupported method {method}")

        result["ws_url"] = f"/ws/conflicts/{slug}/"
        return result

    async def post(self, request, slug):
        try:
            conflict_dto: dict[str, Any] = await self._action(
                request, slug, method="post"
            ) # type: ignore
            return Response(conflict_dto, status=201)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception:
            return Response({"error": "Internal server error"}, status=500)

    async def get(self, request, slug):
        try:
            conflict_dto: dict[str, Any] = await self._action(
                request, slug, method="get"
            ) # type: ignore
            return Response(conflict_dto, status=200)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": "Internal server error"}, status=500)

    async def delete(self, request, slug):
        try:
            await self._action(
                request, slug, method="delete"
            )
            return Response(status=204)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": "Internal server error"}, status=500)


class ConflictView(BaseConflictActionView):
    service_method_name = "get_conflict"


class CancelConflictView(BaseConflictActionView):
    service_method_name = "cancel_conflict"


class DeleteConflictView(BaseConflictActionView):
    service_method_name = "delete_conflict"


class CreateOfferTruceView(BaseConflictActionView):
    service_method_name = "create_offer_truce"


class CancelOfferTruceView(BaseConflictActionView):
    service_method_name = "cancel_offer_truce"


class AcceptedOfferTruceView(BaseConflictActionView):
    service_method_name = "accept_offer_truce"
