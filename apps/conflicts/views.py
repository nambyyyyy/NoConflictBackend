from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.conflicts.models import Conflict, ConflictItem
from apps.conflicts.serializers import ConflictSerializer, ConflictItemSerializer
from apps.common.permissions import IsOwnerOnly, IsOwnerOrRead


class ConflictView(APIView):
    serializer_class = ConflictSerializer
    permission_classes = [IsOwnerOnly]

    def get(self, request):
        # GET: Возвращает данные для формы + подтянутые ConflictItem
        # Здесь полный контроль: собираем данные вручную

        # Подтягиваем доступные items (пример: items юзера без привязанного конфликта)
        try:
            user_items = ConflictItem.objects.filter(
                user=request.user, conflict__isnull=True
            )
            items_serializer = ConflictItemSerializer(user_items, many=True)
            available_items = items_serializer.data
        except (
            Exception
        ) as e:
            return Response(
                {"error": "Ошибка подтягивания items: " + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        status_choices = [choice[0] for choice in Conflict.STATUS_CHOICES]

        response_data = {
            "available_items": available_items,  # Список для выбора в форме
            "status_choices": status_choices,
        }
        return Response(response_data, status=status.HTTP_200_OK)
