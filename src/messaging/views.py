from rest_framework.response import Response
from rest_framework.generics import CreateAPIView , ListAPIView
from rest_framework.views import APIView
from rest_framework import status
from django.db import models
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import Message , Chat
from .serializers import MessageSerializer , ChatSerializer
from Accounts.models import Account

class ChatListView(ListAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    

class ChatMessagesView(APIView):
    
    def get(self , request , chat_id):
        
        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return Response({"error": "Chat Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        messages = chat.messages.all().order_by('sent_at')
        
        serializer = MessageSerializer(messages , context={"request":request} , many=True)
        
        
        return Response({"messages" : serializer.data})


class SendMessageView(APIView):
    
    def post(self, request , recipient_id):
        content = request.data.get('content', '').strip()
        
        if not recipient_id or not content:
            return Response({"error": "recipient id and Message content is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            recipient = Account.objects.get(id=recipient_id)
        except Account.DoesNotExist:
            return Response({"error": "Recipient Not Found"}, status=status.HTTP_404_NOT_FOUND)

        chat = self.get_or_create_chat(request.user , recipient)

        message = Message.objects.create(chat=chat, sender=request.user, content=content)

        chat.save()
        
        serializer = MessageSerializer(message, context={"request":request})
        
        channel_layer = get_channel_layer()
        
        async_to_sync(channel_layer.group_send)(
            f'chat_{chat.id}',
            {
                'type': 'chat_message',  # Calls chat_message() in consumer
                'message': {
                    'type': 'new_message',
                    'data': serializer.data
                }
            }
        )
        return Response({"message": "Message sent successfully","chat_id": chat.id,
                         "message": serializer.data,"chat_created": getattr(chat, '_created', False)},
                        status=status.HTTP_201_CREATED)
        
        
        
    def get_or_create_chat(self, user1, user2):

        existing_chat = Chat.objects.filter(
            participants=user1
        ).filter(
            participants=user2
        )
        
        if existing_chat:
            for chat in existing_chat:
                if chat.participants.count() == 1 and user1 == user2:
                    return chat
                if chat.participants.count() ==  2:
                    return chat
        
        
        new_chat = Chat.objects.create()
        new_chat.participants.add(user1, user2)
        new_chat._created = True
        return new_chat
    
    
    
    

@api_view(['GET'])
@permission_classes([])
def chat_room_view(request, chat_id):
    """Render chat room page"""
    # Verify user has access to this chat
    print("------------------------------------")
    print(chat_id)
    print(type(chat_id))
    # try:
    #     chat = Chat.objects.filter(id=chat_id, participants=request.user)
    #     print("after finding chat")
    # except Chat.DoesNotExist:
    #     return Response({"error": "Chat not found"}, status=404)
    
    # print("before token")
    # Get access token (if using JWT)
    # You might need to generate a new token or get from request
    # from rest_framework_simplejwt.tokens import AccessToken
    # access_token = str(AccessToken.for_user(request.user))
    
    print("After token")
    context = {
        'chat_id': chat_id,
        # 'chat': ChatSerializer(chat).data,
        # 'access_token': access_token,
    }
    
    print("after context")
    return render(request, 'chat.html', context)