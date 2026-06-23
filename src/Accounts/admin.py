from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Account

@admin.register(Account)
class CustomUserAdmin(UserAdmin):
    model = Account
    list_display = ("id" , "email", "username", "phone_number" , "is_staff")
    ordering = ("username",)
    search_fields = ("username", "email" , "phone_number")

    readonly_fields = ["date_joined" , "last_seen" , "is_online"]
    fieldsets = (
        (None, {"fields": ("email", "username" , "phone_number" , "display_name" , "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser")}),
        (None , {"fields" :("date_joined" , "last_seen" , "is_online")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "password1", "password2"),
        }),
    )
    
