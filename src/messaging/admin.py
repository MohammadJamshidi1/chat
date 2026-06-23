from django.contrib import admin

from .models import Chat , Message

# admin.site.register(Chat)
admin.site.register(Message)


@admin.register(Chat)
class CustomChatAdmin(admin.ModelAdmin):
    model = Chat
    list_display = ("id" , "chat_name" , "updated_at", "created_at")
    ordering = ("-updated_at",)
    search_fields = ("updated_at" , "id")
    readonly_fields = ["updated_at" , "created_at"]
    filter_horizontal = ("participants",) 
    
    def chat_name(self , obj):
        return str(obj)
            