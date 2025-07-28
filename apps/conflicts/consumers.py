import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ConflictConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Вызывается, когда клиент пытается установить WebSocket-соединение.
        """
        # 1. Извлекаем slug из URL
        self.conflict_slug = self.scope['url_route']['kwargs']['slug']
        self.conflict_group_name = f'conflict_{self.conflict_slug}'
        
        await self.channel_layer.group_add(
            self.conflict_group_name,
            self.channel_name
        )
        await self.accept()
        
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.conflict_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        await self.channel_layer.group_send(
            self.conflict_group_name,
            {
                'type': 'broadcast_message', # Имя метода-обработчика, который будет вызван
                'message': f"Echo: {text_data}"
            }
        )
        
    async def broadcast_message(self, event):
        """
        Этот метод вызывается у КАЖДОГО консьюмера в группе,
        когда кто-то отправляет сообщение в эту группу.
        """
        message = event['message']

        # Отправляем сообщение обратно клиенту через WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))