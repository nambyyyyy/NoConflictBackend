from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.conflicts.models import Conflict, ConflictItem
from apps.conflicts.serializers import ConflictSerializer, ConflictItemSerializer
from apps.common.permissions import IsOwnerOnly, IsOwnerOrRead
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

class ConflictCreateView(APIView):
    """Представление для создания конфликта"""
    
    serializer_class = ConflictSerializer
    permission_classes = [IsOwnerOnly]

    def get(self, request):
        # GET: Возвращает данные для формы + подтянутые ConflictItem
        # Подтягиваем доступные items (пример: items юзера без привязанного конфликта)
        try:
            user_items = ConflictItem.objects.filter(
                user=request.user, conflict__isnull=True
            ).prefetch_related('point').order_by('-created_at')
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
            item_ids = request.data.get('item_ids', [])
            if not item_ids:
                raise ValidationError("Не выбрано ни одного item для конфликта.")
        
            items = ConflictItem.objects.filter(id__in=item_ids, user=request.user, conflict__isnull=True)
            if not items.exists():
                raise ValidationError("Выбранные items не найдены или уже привязаны.")
        
            items.update(conflict=conflict)  # Привязываем
        
            # Обработка партнёра: два сценария
            partner_id = request.data.get('partner_id')
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














