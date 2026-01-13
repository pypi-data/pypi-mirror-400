from django.urls import path
from .views import Mail, ChangePasswordAPIView, LoginsAPIView, RegisterView, LogoutAPIView, SetNewPasswordAPIView, VerifyEmail, LoginAPIView, PasswordTokenCheckAPI, RequestPasswordResetEmail
from rest_framework_simplejwt.views import (TokenRefreshView,)


from django.urls import path, include
from .views import getPhoneNumberRegistered, getPhoneNumberRegistered_TimeBased


urlpatterns = [
    path("register/numero/i", getPhoneNumberRegistered.as_view(), name="OTP_Sem_Limite_De_Tempo"),
    path("register/numero/l", getPhoneNumberRegistered_TimeBased.as_view(), name="OTP_Com_Limite_De_Tempo"),

    path('register/', RegisterView.as_view(), name="register"),
    path('login/', LoginAPIView.as_view(), name="login"),
    path('changepassword/', ChangePasswordAPIView.as_view(), name="changepassword"),
    path('logins/', LoginsAPIView.as_view(), name="logins"),
    path('logout/', LogoutAPIView.as_view(), name="logout"),
    path('email-verify/', VerifyEmail.as_view(), name="email-verify"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('request-reset-email/', RequestPasswordResetEmail.as_view(), name="request-reset-email"),
    path('password-reset/<uidb64>/<token>/', PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),# ainda
    path('password-reset-complete', SetNewPasswordAPIView.as_view(), name='password-reset-complete'),
    path('email', Mail.as_view(), name='email')
]

