from django.urls import path
from rest_framework_simplejwt.views import (TokenRefreshView,)
from django.urls import path, include
from .views import *

from django.urls import path, include
from .import viewsApi, views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'idiomas', viewsApi.IdiomaAPIView)
router.register(r'inputs', viewsApi.InputAPIView)
router.register(r'strings', viewsApi.StringAPIView)
router.register(r'users', viewsApi.UsuarioAPIView)

router.register(r'tipoEntidades', viewsApi.TipoEntidadeAPIView)
router.register(r'entidades', viewsApi.EntidadeAPIView)
router.register(r'sucursals', viewsApi.SucursalAPIView)
router.register(r'grupos', viewsApi.GrupoAPIView)
router.register(r'permissions', viewsApi.PermissionAPIView)
router.register(r'modelos', viewsApi.ModeloAPIView)
router.register(r'ficheiros', viewsApi.FicheiroAPIView)



   


urlpatterns = [
    path('', include(router.urls)),

    path("register/numero/i", getPhoneNumberRegistered.as_view(), name="OTP_Sem_Limite_De_Tempo"),
    path("register/numero/l", getPhoneNumberRegistered_TimeBased.as_view(), name="OTP_Com_Limite_De_Tempo"),

    path('register/', RegisterView.as_view(), name="register"),
    path('login/', LoginAPIView.as_view(), name="login"),
    path('logout/', LogoutAPIView.as_view(), name="logout"),
    path('me/', MeAPIView.as_view(), name="me"),
    path('change_password_email/', ChangePasswordEmailAPIView.as_view(), name="change_password_email"),
    path('email_verify/', VerifyEmail.as_view(), name="email_verify"),
    path('refresh_token/', TokenRefreshView.as_view(), name='refresh_token'),



    path('logins/', LoginsAPIView.as_view(), name="logins"),
    path('request_reset_email/', RequestPasswordResetEmail.as_view(), name="request_reset_email"),
    path('password_reset/<uidb64>/<token>/', PasswordTokenCheckAPI.as_view(), name='password_reset_confirm'),# ainda
    path('password_reset_complete', SetNewPasswordAPIView.as_view(), name='password_reset_complete'),
    path('email', Mail.as_view(), name='email'),
    path('change_password_mobile/', ChangePasswordEmailAPIView.as_view(), name="change_password_mobile"),

]






