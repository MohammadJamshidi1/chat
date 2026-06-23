from django.db import models
import uuid
import os
from django.contrib.auth.models import AbstractBaseUser , BaseUserManager , PermissionsMixin
from django.apps import apps
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class AccountManager(BaseUserManager):
    def _create_user(self, username, email, password, **extra_fields):

        if not username:
            raise ValueError("The given username must be set")
        if not email:
            raise ValueError("The given email must be set")
        
        email = self.normalize_email(email)

        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username , email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, email, password, **extra_fields)

    
    def get_by_natural_key(self , identifier):
        return self.get(models.Q(username__iexact=identifier) | models.Q(email__iexact=identifier))
    


def file_dir_path(instance , filename):
    return f"user_{instance.user.pk}/{filename}"

def image_validate(image):
    file_size = image.file
    max_size = 5
    
    if file_size > max_size * 1024 * 1024:
        raise ValidationError(f"Max size of file is {max_size} MB")
    
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    extension = os.path.splitText(image.name)[1]
    if not extension.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')

class Account(AbstractBaseUser , PermissionsMixin):
    username = models.CharField(unique=True, max_length=60)
    email = models.EmailField(unique=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(unique=True, max_length=20)
    display_name = models.CharField(max_length=60, blank=True, null=True)
    avatar = models.ImageField(upload_to=file_dir_path, blank=True, null=True , validators=[image_validate])
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(blank=True, null=True)
    show_last_seen = models.BooleanField(default=True)
    allow_unknown_contacts = models.BooleanField(default=True)
    date_joined = models.DateTimeField("date joined", default=timezone.now)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    objects = AccountManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email' , 'phone_number']
    
    def __str__(self):
        return self.username

    

class DeviceToken(models.Model):
    user = models.ForeignKey(Account , on_delete=models.CASCADE)
    device_id = models.CharField(max_length=50 , unique=True , default=uuid.uuid4)
    device_name = models.CharField(max_length=100)
    refresh_token = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return f"{self.user.username} - {self.device_id}"