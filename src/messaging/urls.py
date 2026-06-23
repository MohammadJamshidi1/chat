from django.urls import path

from . import views

urlpatterns = [
    path('chats/' , views.ChatListView.as_view()),
    path('chats/<int:chat_id>/messages/' , views.ChatMessagesView.as_view()),
    path('chats/<int:recipient_id>/send_message/' , views.SendMessageView.as_view()),
    
    path('chats/<int:chat_id>/room/', views.chat_room_view, name='chat-room'),
]