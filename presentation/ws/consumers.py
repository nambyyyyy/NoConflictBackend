import json
from typing import Any
from django.db import transaction
from channels.generic.websocket import AsyncWebsocketConsumer
from presentation.dependencies.service_factories import get_conflict_service
from application.services.conflict_service import ConflictService
from core.entities.conflict import ConflictError
from application.dtos.conflict_dto import ConflictItemDTO
from rest_framework.response import Response


class ConflictConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Получаем slug из URL
        self.slug = self.scope["url_route"]["kwargs"]["slug"]  # type: ignore
        self.room_group_name = f"conflict_{self.slug}"

        user = self.scope["user"]  # type: ignore
        if user.is_anonymous:  # type: ignore
            await self.close()
            return

        try:
            conflict_service: ConflictService = get_conflict_service()
            await conflict_service.get_conflict(user.id, self.slug)
        except ConflictError:
            await self.close()
            return

        # Подключаемся к группе
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        """
        Вызывается при получении сообщения от клиента по WebSocket.
        """
        if text_data is None:
            return

        try:
            data: dict[str, Any] = json.loads(text_data)
        except (json.JSONDecodeError, TypeError):
            await self.send(text_data=json.dumps({"error": "Invalid JSON"}))
            return

        event_type = data.pop("event_type", None)
        user_id = data.pop("user_id", None)
        slug = data.pop("slug", None)
        item_id = data.pop("item_id", None)
        new_value = data.pop("new_value", None)

        try:
            conflict_service: ConflictService = get_conflict_service()
            item_dto: ConflictItemDTO = await conflict_service.update_item(
                event_type, user_id, slug, item_id, new_value, transaction.atomic
            )
            # Откорректировать
            return Response(item_dto.__dict__, status=201)
        except Exception:
            # Дописать
            pass

    # async def send_update(self, event):
    #     data = event["data"]
    #     await self.send(text_data=json.dumps(data))
