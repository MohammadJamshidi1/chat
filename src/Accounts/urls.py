from django.urls import path

from . import views


urlpatterns = [
    path('create/' , views.CreateAccount.as_view()),
    path('login/' , views.LoginUser.as_view()),
    path('update/<int:pk>/' , views.UpdateAccount.as_view()),
    path('logout/' , views.LogoutUser.as_view()),
    path('refresh_token/' , views.RefreshTokenView.as_view()),
]
