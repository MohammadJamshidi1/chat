import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone


from .models import Chat , Message
from Accounts.models import Account
from .serializers import MessageSerializer


logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.chat_group_name = f"chat_{self.chat_id}"
        self.user = self.scope['user']
        
        if self.user == AnonymousUser:
            await self.close(code=4001)
            return
        
        has_access = await self.check_chat_access()
        if not has_access:
            await self.close(code=4003)
            return
        
        
        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )
        
        await self.accept()

        await self.update_user_online_status(True)

        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'user_status',
                'message': {
                'type': 'user_online',
                'user_id': self.user.id,
                'username': self.user.username
            }
        }
        )
    
        logger.info(f"User {self.user.username} connected to chat {self.chat_id}")
        
    async def disconnect(self, code):
        
        if hasattr(self , "chat_group_name"):
            
            await self.channel_layer.group_discard(
                self.chat_group_name,
                self.channel_name
            )
        
        await self.update_user_online_status(False)
        
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'user_status',
                'message': {
                    'type': 'user_offline',
                    'user_id': self.user.id,
                    'username': self.user.username
                }
            }
        )

        logger.info(f"User {self.user.username} disconnected from chat {self.chat_id}")
        
        
    async def receive(self, text_data):
        
        try:
            data = json.loads(text_data)
            print("================================")
            print("text data : ")
            print(text_data)
            print("================================")
            message_type = data.get("type")
            
            if message_type == 'chat_message':
                await self.handle_chat_message(data)
            # elif message_type == 'typing_start':
            #     await self.handle_typing_start()
            # elif message_type == 'typing_stop':
            #     await self.handle_typing_stop()
            # elif message_type == 'mark_read':
            #     await self.handle_mark_read(data)
            
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                "type" : "error",
                "message" : "Invalid JSON"
            }))
            
        
    async def handle_chat_message(self , data):
        content = data.get("message" , "").strip()
        if not content:
            return
        
        message = await self.save_message(content)
        if not message:
            return
        
        message_data = await self.serialize_message(message)
        
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                "type" : "chat_message",
                "message" : {
                    "type" : "new_message",
                    "data" : message_data.data
                }
            }
        )
        
    
    async def handle_typing_start(self):
        
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                "type" : "typing_status",
                "message" : {
                    "type" : "typing_start",
                    "user_id" : self.user.id,
                    "username" : self.user.username
                }
            }
        )
        
    
    async def handle_typing_stop(self):
        
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                "type" : "typing_status",
                "message" : {
                    "type" : "typing_stop",
                    "user_id" : self.user.id,
                    "username" : self.user.username
                }
            }
        )
        
    
    async def handle_mark_read(self, data):
        
        message_id = data.get("message_id")
        if message_id:
            await self.mark_message_read(message_id)
            
            
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

    
    async def typing_status(self , event):
        if event["message"]["user_id"] != self.user.id:
            await self.send(text_data=json.dumps(event["message"]))
            
    async def user_status(self , event):
        if event["message"]["user_id"] != self.user.id:
            await self.send(text_data=json.dumps(event["message"]))

    
    @database_sync_to_async
    def check_chat_access(self):
        
        try:
            Chat.objects.get(id=self.chat_id , participants=self.user)
            return True
        except Chat.DoesNotExist:
            return False
        
        
    @database_sync_to_async
    def save_message(self, content):
        
        try:
            chat = Chat.objects.get(id=self.chat_id , participants=self.user)
            message = Message.objects.create(
                chat=chat,
                sender=self.user,
                content=content
            )
            
            chat.save()
            return message
        except Chat.DoesNotExist:
            return None
        
    
    @database_sync_to_async
    def serialize_message(self, message):
        serializer = MessageSerializer(message)
        return serializer
    
    @database_sync_to_async
    def mark_message_read(self, message_id):
        
        try:
            message = Message.objects.get(id=message_id)
            # add
        except Message.DoesNotExist:
            pass
        
    @database_sync_to_async
    def update_user_online_status(self, is_online):
        
        self.user.is_online = is_online
        if not is_online:
            self.user.last_seen = timezone.now()
        
        self.user.save(update_fields=["is_online", "last_seen"])