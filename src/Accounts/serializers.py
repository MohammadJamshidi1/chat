from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Account



class CreateAccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type':'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type':'password'})
    
    class Meta:
        model = Account
        fields = [
            "username",
            "email",
            "phone_number",
            "password",
            "confirm_password",
            "display_name"
        ]
        
        extra_kwargs = {
            "email": {"required": True},
            "phone_number": {"required": True},
        }
        
    
    def validate_password(self , value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters")
        if not value.replace('_', '').replace('-', '').isalnum():
            raise serializers.ValidationError("Username can only contain letters, numbers, hyphens and underscores")
        return value.lower()

    def validate_email(self, value):
        if Account.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists")
        return value.lower()
    
    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    
    def create(self, validated_data):
        password = validated_data.pop("password" , None)
        confirm_password = validated_data.pop("confirm_password" , None)
        
        user = Account(**validated_data)
        
        if password and password == confirm_password:
            user.set_password(password)
        user.save()
        return user
    
    

class AccountSerializer(serializers.ModelSerializer):
    avatar_url = serializers.ReadOnlyField()
    
    class Meta:
        model = Account
        fields = [
            'id',
            'username', 
            'email',
            'phone_number',
            'display_name',
            'avatar',
            'avatar_url',
            'is_online',
            'last_seen',
            'date_joined',
            'show_last_seen',
            'allow_unknown_contacts'
        ]
        
        read_only_fields = [
            'id',
            'date_joined', 
            'last_seen',
            'is_online'
        ]
        
        extra_kwargs = {
            'email': {'required': False},
            'phone_number': {'required': False},
        }
        
        
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")

        if request and request.user != instance:
            
            if not instance.show_last_seen:
                data.pop("last_seen")
                
            data.pop("email" , None)
            data.pop("phone_number" , None)
            
        return data