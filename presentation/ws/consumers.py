import json
from uuid import UUID
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from presentation.dependencies.service_factories import get_conflict_service
from application.services.conflict_service import ConflictService
from core.entities.conflict import ConflictError

UserModel = get_user_model()

class ConflictConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Получаем slug из URL
        print(self.__dict__)      
        print(self.scope)
        
        self.slug = self.scope['url_route']['kwargs']['slug']
        self.room_group_name = f'conflict_{self.slug}'

        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()
            return
            
        try:
            conflict_service: ConflictService = get_conflict_service()
            await sync_to_async(
                lambda: conflict_service.get_conflict(user.id, self.slug)
            )()
        except ConflictError:
            await self.close()
            return

        # Подключаемся к группе
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    # async def disconnect(self, close_code):
    #     await self.channel_layer.group_discard(
    #         self.room_group_name,
    #         self.channel_name
    #     )

    # async def receive(self, text_data):
    #     # Обработка сообщений от клиента (например, "я начал редактировать")
    #     pass

    # # Этот метод будет вызываться при отправке события в группу
    # async def send_update(self, event):
    #     data = event["data"]
    #     await self.send(text_data=json.dumps(data))