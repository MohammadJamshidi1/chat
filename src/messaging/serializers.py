from rest_framework import serializers

from Accounts.serializers import AccountSerializer
from .models import Message , Chat


class MessageSerializer(serializers.ModelSerializer):
    sender = AccountSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ["id" , "content" , "sender" , "sent_at"]
        read_only_fields = ["id" , "sender" , "sent_at"]
        

class ChatSerializer(serializers.ModelSerializer):
    participants = AccountSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Chat
        fields = ['id', 'participants', 'created_at', 'last_message']
        read_only_fields = ['id', 'created_at']
        
    
    def get_last_message(self , obj):
        last_msg = obj.messages.last()
        if last_msg:
            return MessageSerializer(last_msg).data
        return None