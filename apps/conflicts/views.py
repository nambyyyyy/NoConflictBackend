from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Conflict
from .serializers import ConflictListSerializer, ConflictDetailSerializer
from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins

User = get_user_model()


class ConflictViewSet(
    mixins.CreateModelMixin,   # Добавляет только действие .create() (для POST)
    mixins.RetrieveModelMixin, # GET для одного конфликта
    mixins.ListModelMixin,     # GET для списка конфликтов
    viewsets.GenericViewSet    # Базовый класс для ViewSet без каких-либо действий
):
    """
    ViewSet для управления Конфликтами.
    """
    serializer_class = ConflictDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'
    
    def get_queryset(self):
        """
        Этот метод гарантирует, что пользователь увидит только те конфликты,
        в которых он является создателем или партнером.
        """
        # Используем наш готовый менеджер из модели Conflict
        return Conflict.get_for_user(self.request.user).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'list':
            # Если запрос на список - используем простой сериализатор
            return ConflictListSerializer
        return ConflictDetailSerializer
    

    def perform_create(self, serializer):
        """
        Этот метод-хук вызывается внутри .create() из CreateModelMixin
        сразу после валидации данных, но перед вызовом serializer.save().

        Это идеальное место, чтобы добавить в данные то, что мы не можем
        получить от клиента, но знаем на сервере, — например, текущего пользователя.
        """
        # Мы передаем `creator` в метод .save() сериализатора.
        # Эти данные попадут в `validated_data` внутри метода .create()
        # нашего сериализатора, но уже после основной валидации.
        serializer.save(creator=self.request.user)
    









# Старое
class ConflictCreateView(APIView):
    """Представление для создания конфликта"""

    serializer_class = ConflictSerializer
    permission_classes = [IsOwnerOnly]

    def get(self, request):
        # GET: Возвращает данные для формы + подтянутые ConflictItem
        # Подтягиваем доступные items (пример: items юзера без привязанного конфликта)
        try:
            user_items = (
                ConflictItem.objects.filter(user=request.user, conflict__isnull=True)
                .prefetch_related("point")
                .order_by("-created_at")
            )
            items_serializer = ConflictItemSerializer(user_items, many=True)
            available_items = items_serializer.data
        except Exception as e:
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

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Данные не валидны.", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Создаём конфликт
            conflict = serializer.save(creator=request.user)

            # Привязка выбранных items
            item_ids = request.data.get("item_ids", [])
            if not item_ids:
                raise ValidationError("Не выбрано ни одного item для конфликта.")

            items = ConflictItem.objects.filter(
                id__in=item_ids, user=request.user, conflict__isnull=True
            )
            if not items.exists():
                raise ValidationError("Выбранные items не найдены или уже привязаны.")

            items.update(conflict=conflict)  # Привязываем

            # Обработка партнёра: два сценария
            partner_id = request.data.get("partner_id")
            invite_link = None
            if partner_id:
                # Сценарий 1: существующий партнёр выбран из списка
                try:
                    partner = User.objects.get(id=partner_id)
                    # Здесь добавим уведомление партнеру в личный кабинет (через signals)
                except User.DoesNotExist:
                    raise ValidationError("Выбранный партнёр не существует.")
            else:
                # Сценарий 2: партнёра нет — генерируем уникальную ссылку для приглашения
                invite_link = f"https://noconflict.com/join-conflict/{conflict.slug}/"

            response_data = {
                "slug": conflict.slug,
                "status": "pending",
                "invite_link": invite_link,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        except ValidationError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Логируй для дебагa (в проде используй logging)
            print(f"Ошибка: {e}")  # Замени на logger.error
            return Response(
                {"error": "Ошибка при создании конфликта."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ConflictDetailView(APIView):
    """Представление для действий с конфликтом"""

    permission_classes = [IsOwnerOnly]

    def _get_conflict(self, **kwargs):
        conflict_id = kwargs.get("pk")

        if not conflict_id:
            return Response(
                {"error": "Неверный id конфликта"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            conflict = Conflict.objects.get(pk=conflict_id, is_deleted=False)
        except Conflict.DoesNotExist:
            return Response(
                {"error": "Конфликт не найден или удален"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return conflict

    def _serialization_conflict(self, conflict, user):
        serializer = ConflictSerializer(conflict)
        data = serializer.data
        data["cancelled_by"] = user.username
        return data

    def get(self, request, *args, **kwargs):
        # Получение конфликта
        conflict = self._get_conflict(**kwargs)
        if isinstance(conflict, Response):
            return conflict

        if (request.user == conflict.creator and conflict.deleted_by_creator) or (
            request.user == conflict.partner and conflict.deleted_by_partner
        ):
            return Response(
                {"error": "Конфликт удален"},
                status=status.HTTP_404_NOT_FOUND,
            )

        conflict_items = (
            ConflictItem.objects.filter(conflict=conflict)
            .prefetch_related("point")
            .order_by("-created_at")
        )
        return Response(1, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        # Отмена конфликта
        conflict = self._get_conflict(**kwargs)
        if isinstance(conflict, Response):
            return conflict

        try:
            conflict.cancel()
            if conflict.partner:
                # Здесь должно быть уведомление от отмене второму юзеру (если он уже подключен)
                pass
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

        data = self._serialization_conflict(conflict=conflict, user=request.user)
        return Response(data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        # Удаление конфликта
        conflict = self._get_conflict(**kwargs)
        if isinstance(conflict, Response):
            return conflict

        if conflict.status not in ("resolved", "cancelled", "abandoned"):
            return Response(
                {"error": "Можно удалить только после завершения или отмены"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            conflict.soft_delete_for_user(user=request.user)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_200_OK)
