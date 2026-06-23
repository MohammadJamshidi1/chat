from rest_framework.generics import CreateAPIView , UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.utils import timezone
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
import uuid
import logging

from .utils import get_device_info
from .models import Account , DeviceToken
from .serializers import AccountSerializer , CreateAccountSerializer

logger = logging.getLogger(__name__)

class CreateAccount(CreateAPIView):
    queryset = Account.objects.all()
    serializer_class = CreateAccountSerializer
    permission_classes = []
    
@method_decorator(ratelimit(key='ip' , rate='5/m' , method='POST') , name='post')
class LoginUser(APIView):
    permission_classes = []
    
    def post(self, request):
        ip_address = request.META.get("REMOTE_ADDR")
        user_agent = request.META.get("HTTP_USER_AGENT" , 'Unknown')
        identifier = request.data.get("username") or request.data.get("email")
        password = request.data.get("password")
        
        if not identifier or not password:
            return Response({"error": "Username/email and password are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        print(identifier)
        print("-------------------------")
        print(password)

        user = authenticate(request , username=identifier , password=password)

        if user is None:
            
            logger.warning(
                f"Failed login attempt - IP: {ip_address}, "
                f"Identifier: {identifier}, "
                f"User-Agent: {user_agent}"
            )
            return Response({"error": "Invalid credentials"},  status=status.HTTP_401_UNAUTHORIZED) 
        
        logger.info(
            f"Successful login - User: {user.username}, "
            f"IP: {ip_address}, "
            f"Device: {get_device_info(request)}"
        )
        refresh = RefreshToken.for_user(user)
        
        device_name = get_device_info(request)
        device_id = str(uuid.uuid4())
        
        device_token , created = DeviceToken.objects.get_or_create(user=user , device_name=device_name , device_id=device_id , refresh_token=str(refresh))
        
        if not created:
            device_token.refresh_token = refresh
            device_token.device_id = str(uuid.uuid4())
            device_token.save()
            
        return Response({
            "success": True,
            "data": {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "device_info": {
                    "device_name": device_name,
                    "device_id": device_id
                },
                "user_id": user.pk
            }
        })
        

class UpdateAccount(UpdateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    
class LogoutUser(APIView):
    def post(self , request):
        token = request.data.get("refresh_token")
        DeviceToken.objects.filter(refresh_token=token).delete()
        return Response({"Success" : "Device Logged Out"})
    
    
    
class RefreshTokenView(APIView):
    permission_classes = []
    
    def post(self , request):
        token = request.data.get("refresh_token")
        device_id = request.data.get("device_id")
        
        if not token or not device_id:
            return Response({"error": "Refresh token and device_id required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            device_token = DeviceToken.objects.get(refresh_token=token , device_id=device_id)
        except DeviceToken.DoesNotExist:
             return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

        try:

            refresh = RefreshToken(token)
  
            access_token = str(refresh.access_token)
            
            device_token.last_used = timezone.now()
            device_token.save(update_fields=["last_used"])
            
            return Response({"access_token" : access_token})
        except Exception:
            device_token.delete()
            return Response({"error": "Token expired or invalid login again"}, status=status.HTTP_401_UNAUTHORIZED)
        
        
    