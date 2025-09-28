from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.common.permissions import IsOwnerOrPartner
from apps.conflicts.models import ConflictModel, ConflictEvent
from apps.conflicts.serializers import ConflictListSerializer, ConflictDetailSerializer
from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins
from rest_framework.serializers import Serializer
from django.db.models import QuerySet
from typing import Type
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from asgiref.sync import async_to_sync

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
    permission_classes = [IsOwnerOrPartner]
    lookup_field = 'slug'

    def get_queryset(self) -> QuerySet[ConflictModel]: # type: ignore
        """
        Этот метод гарантирует, что пользователь увидит только те конфликты,
        в которых он является создателем или партнером.
        """
        # Используем наш готовый менеджер из модели Conflict
        return ConflictModel.get_for_user(self.request.user).order_by('-created_at')

    def get_serializer_class(self) -> Type[Serializer]: # type: ignore
        if self.action == 'list':
            # Если запрос на список - используем простой сериализатор
            return ConflictListSerializer
        return ConflictDetailSerializer
     
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conflict_instance = serializer.save(creator=self.request.user)    
        response_data = self.get_serializer(conflict_instance).data
    
    # Добавление ссылки-приглашения, если нужно.
        if not conflict_instance.partner:
            invite_link = request.build_absolute_uri(f'/conflicts/{conflict_instance.slug}/join-page/')
            response_data['invite_link'] = invite_link
        else:
        # Тут логика уведомления для существующего партнера
            pass

        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)    

    @action(
        detail=True,          # Действие выполняется над ОДНИМ объектом (детальный URL)
        methods=['post'],     # HTTP-метод, который будет вызывать это действие
    )
    def join(self, request, slug=None):
        conflict, user = self.get_object(), request.user

        try:
            with transaction.atomic():
                conflict.add_partner(request.user)
                conflict.save()
                create_event_sync = async_to_sync(ConflictEvent.acreate_event)  
                create_event_sync(conflict=conflict, initiator=user, event_type='conflict_join_success')           
        except (ValidationError, IntegrityError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance=conflict)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @action(
        detail=True,      # Действие над ОДНИМ объектом
        methods=['post'], # POST - это стандарт для изменения состояния ресурса
        url_path='cancel' # Явное имя для URL, чтобы не пересекалось с методом модели
    )
    def cancel_conflict(self, request, slug=None):
        conflict, user = self.get_object(), request.user

        is_creator = (request.user == conflict.creator)
        is_partner = (conflict.partner is not None and request.user == conflict.partner)

        if not (is_creator or is_partner):
            return Response(
                {'error': 'Вы не являетесь участником этого конфликта.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            with transaction.atomic():
                conflict.cancel()
                conflict.save()
                create_event_sync = async_to_sync(ConflictEvent.acreate_event)  
                create_event_sync(conflict=conflict, initiator=user, event_type='conflict_cancel')
        except (ValidationError, IntegrityError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(conflict)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def destroy(self, request, *args, **kwargs):
        conflict, user = self.get_object(), request.user
        
        try:
            with transaction.atomic():
                conflict.soft_delete_for_user(user=user)
                conflict.save()
                create_event_sync = async_to_sync(ConflictEvent.acreate_event)  
                create_event_sync(conflict=conflict, initiator=user, event_type='conflict_delete') 
        except (ValidationError, IntegrityError) as e:
            # Ловим ошибку, если конфликт уже был удален.
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
    # Кнопка примирения 
    @action(detail=True, methods=['post'], url_path='propose-truce')
    def propose_truce(self, request, slug=None):
        # Эндпоинт обработки запроса на мир
        conflict, user = self.get_object(), request.user
        
        try:
            with transaction.atomic():
                conflict.validate_truce_proposal(user=user)
                conflict.truce_initiator = user
                conflict.truce_status = 'pending'
                conflict.save()
                create_event_sync = async_to_sync(ConflictEvent.acreate_event)  
                create_event_sync(conflict=conflict, initiator=request.user, event_type='truce_proposed')
        except (ValidationError, IntegrityError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        
        
        # 3. Отправляем WebSocket-уведомление ДРУГОМУ участнику
        # target_user = conflict.partner if user == conflict.creator else conflict.creator
        # send_websocket_notification(to=target_user, type='truce_proposed')
        
        return Response(self.get_serializer(conflict).data, status=200)
        
    
    @action(detail=True, methods=['post'], url_path='accept-truce')
    def accept_truce(self, request, slug=None):
        # Эндпоинт обработки подтверждения мира
        conflict, user = self.get_object(), request.user
        
        if conflict.truce_status != 'pending' or user == conflict.truce_initiator:
            return Response({"error": "Нет активного предложения для вас"}, status=400)
        
        try:
            with transaction.atomic():
                conflict.resolve(manual=True) # Используем наш старый метод resolve
                conflict.truce_status = 'accepted'
                conflict.save()           
                create_event_sync = async_to_sync(ConflictEvent.acreate_event)          
                create_event_sync(conflict=conflict, initiator=request.user, event_type='truce_accepted')
        except (ValidationError, IntegrityError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
               
        # 3. Отправляем WebSocket-уведомление обоим
        # send_websocket_notification(to_group=..., type='truce_accepted')

        return Response(self.get_serializer(conflict).data, status=200)
    
    @action(detail=True, methods=['post'], url_path='decline-truce')
    def decline_truce(self, request, slug=None):
        # Эндпоинт обработки отказа от мира
        conflict, user = self.get_object(), request.user
        
        if conflict.truce_status != 'pending' or user == conflict.truce_initiator:
            return Response({"error": "Нет активного предложения для вас"}, status=400)
        
        # 2. Сбрасываем статус предложения
        with transaction.atomic():
            conflict.truce_status = 'none'
            conflict.truce_initiator = None
            conflict.save()          
            create_event_sync = async_to_sync(ConflictEvent.acreate_event)
            create_event_sync(conflict=conflict, initiator=request.user, event_type='truce_declined')    

        # 3. Отправляем WebSocket-уведомление инициатору
        # send_websocket_notification(to=conflict.truce_initiator, type='truce_declined')

        return Response(self.get_serializer(conflict).data, status=200)
    
    
