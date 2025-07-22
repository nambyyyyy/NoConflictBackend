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
    mixins.DestroyModelMixin,  # DELETE 
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
    
    @action(
        detail=True,          # Действие выполняется над ОДНИМ объектом (детальный URL)
        methods=['post'],     # HTTP-метод, который будет вызывать это действие
        permission_classes=[IsAuthenticated] # Можно указать отдельные права, если нужно
    )
    def join(self, request, slug=None):
        conflict = self.get_object()
        
        try:
            conflict.add_partner(request.user)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(isinstance=conflict)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(
        detail=True,      # Действие над ОДНИМ объектом
        methods=['post'], # POST - это стандарт для изменения состояния ресурса
        url_path='cancel' # Явное имя для URL, чтобы не пересекалось с методом модели
    )
    def cancel_conflict(self, request, slug=None):
        conflict = self.get_object()

        is_creator = (request.user == conflict.creator)
        is_partner = (conflict.partner is not None and request.user == conflict.partner)
        
        if not (is_creator or is_partner):
            return Response(
                {'error': 'Вы не являетесь участником этого конфликта.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            conflict.cancel()
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(conflict)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        conflict = self.get_object()
        
        try:
            conflict.soft_delete_for_user(user=request.user)
        except ValidationError as e:
            # Ловим ошибку, если конфликт уже был удален.
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(status=status.HTTP_204_NO_CONTENT)




