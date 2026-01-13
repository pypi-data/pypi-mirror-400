from django.shortcuts import render
from django.template import loader
from rest_framework import generics, status, views, permissions
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import auth
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import Group

from .serializers import *
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, UserLogin, TipoEntidade

from django.core.mail import send_mail


# import environ
# from core.SMS import SMS

# Initialise environment variables
# env = environ.Env()
from django.urls import reverse
import jwt
from drf_yasg import openapi
from django.conf import settings

# from .renderers import UserRenderer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

from django.shortcuts import redirect
from django.http import HttpResponsePermanentRedirect
import os
from django.core.mail import EmailMultiAlternatives

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from .classes import UserName
import re


def is_valid_email(email):
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email) is not None

from datetime import datetime

from rest_framework.views import APIView

from .models import User
import base64
import pyotp


# This class returns the string needed to generate the key
class generateKey:
    @staticmethod
    def returnValue(phone):
        print(settings.OTP_KEY)
        print(phone)
        return str(phone) + str(datetime.date(datetime.now())) + settings.OTP_KEY


class getPhoneNumberRegistered(APIView):
    # Get to Create a call for OTP
    @staticmethod
    def post(request):
        phone =  str('+' + request.data["mobile"]).replace('+', '')
        try:
            user = User.objects.get(mobile=phone)  # if mobile already exists the take this else create New One
        except ObjectDoesNotExist:
            if 'reset_senha' in request.query_params:
                return Response({'alert_error': 'O numero nao existe <br><b>' + phone + '</b>'}, status=400)  # Just for demonstration
                
            nome = str(str(request.META['HTTP_ORIGIN']).split('.')[0].upper()).split('/')[-1]
            request.data['username'] = UserName.Create(str(request.data['username'].replace(' ', '_')))
            request.data['mobile'] = phone
            request.data['email'] = None
            serializer = RegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            user_data = serializer.data
            user = User.objects.get(mobile=phone)
            tipoEntidade = TipoEntidade.objects.get(nome=str(nome).capitalize())

            pessoa = Pessoa()
            pessoa.user= user
            pessoa.save()
            
        user.counter += 1  # Update Counter At every Call
        user.save()
        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(phone).encode())  # Key is generated
        OTP = pyotp.HOTP(key)  # HOTP Model for OTP is created
        try:
            SMS.send(from__ ='+17244014353', to__='+258'+str(phone), text__='Nao partilhe esse codigo:\nOTP '+OTP.at(user.counter))
        except Exception as e:
            return Response({'alert_error': 'Erro<br>'+ str(e) }, status=400)  # Just for demonstration
            
        return Response({'alert_success': 'Enviamos um OTP para o seu numero <br><b>' + phone + '</b>', "OTP": OTP.at(user.counter)}, status=201)  # Just for demonstration

    # This Method verifies the OTP
    @staticmethod
    def put(request):
        phone = str( '+' + request.data["mobile"]).replace('+', '')
        try:
            user = User.objects.get(mobile=phone)
        except ObjectDoesNotExist:
            return Response("User does not exist", status=404)  # False Call

        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(phone).encode())  # Generating Key
        OTP = pyotp.HOTP(key)  # HOTP Model
        if OTP.verify(request.data["otp"], user.counter):  # Verifying the OTP
            user.is_verified_mobile = True
            user.save()
            return Response({'alert_success': 'Voce esta Autorizado!', 'id': user.id, 'otp': request.data["otp"], 'mobile': request.data["mobile"]}, status=202)
        return Response({'alert_error': 'OTP is wrong'}, status=400)


# Time after which OTP will expire
EXPIRY_TIME = 120 # seconds

class getPhoneNumberRegistered_TimeBased(APIView):
    # Get to Create a call for OTP
    @staticmethod
    def get(request, phone):
        phone = '+' + str(phone).replace('+', '')
        try:
            mobile = User.objects.get(mobile=phone)  # if mobile already exists the take this else create New One
        except ObjectDoesNotExist:
            User.objects.create(
                mobile=phone,
            )
            mobile = User.objects.get(mobile=phone)  # user Newly created Model
        mobile.save()  # Save the data
        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(phone).encode())  # Key is generated
        OTP = pyotp.TOTP(key,interval = EXPIRY_TIME)  # TOTP Model for OTP is created
        print(OTP.now())
        # Using Multi-Threading send the OTP Using Messaging Services like Twilio or Fast2sms
        SMS.send(from__='+13192205575', to__=phone, text__='Nao partilhe esse codigo:\nOTP '+OTP.now())
        return Response({"OTP": OTP.now()}, status=200)  # Just for demonstration

    # This Method verifies the OTP
    @staticmethod
    def post(request, phone):
        phone = '+' + str(phone).replace('+', '')
        try:
            mobile = User.objects.get(mobile=phone)
        except ObjectDoesNotExist:
            return Response("User does not exist", status=404)  # False Call

        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(phone).encode())  # Generating Key
        OTP = pyotp.TOTP(key,interval = EXPIRY_TIME)  # TOTP Model 
        if OTP.verify(request.data["otp"]):  # Verifying the OTP
            mobile.isVerified = True
            mobile.save()
            return Response("You are authorised", status=200)
        return Response("OTP is wrong/expired", status=400)



























class CustomRedirect(HttpResponsePermanentRedirect):
    allowed_schemes = [os.environ.get('APP_SCHEME'), 'http', 'https']


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    # renderer_classes = (UserRenderer,)

    def post(self, request):
        origin = request.META.get("HTTP_ORIGIN", 'http://mytech.co.mz')
        nome = str(str(origin).split('.')[0].upper()).split('/')[-1]

        data = request.data.copy()
        data['username'] = UserName.Create(str(request.data['username'].replace(' ', '_')))
        data['mobile'] = None
        user = data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data

        user = User.objects.get(email=user_data['email'])
        tipoEntidade = TipoEntidade.objects.get(nome=str(nome).capitalize())
        logo = FullPath.url(None, tipoEntidade.icon.name)
        
        token = RefreshToken.for_user(user).access_token

        current_site = get_current_site(request).domain
        relativeLink = reverse('email_verify')
        print(current_site)
  
    
        
        html_message = loader.render_to_string( 'email_confirmacao.html',
            {
                'username': user.username,
                'token': str(token),
                'entidade': nome,
                'tipoentidade': nome,
                'logo': logo,
                'origen': request.META['HTTP_ORIGIN']
            }
        )

        
        email_subject = 'Bem Vindo '+ nome
        to_list = [user.email]
        
        mail = EmailMultiAlternatives(
            subject=email_subject,
            body='Clique no link para restaurar sua senha',
            to=to_list,
        )
        mail.attach_alternative(html_message, "text/html")
          
        try:
            mail.send()
        except Exception as e:
            print(e, end="\n")
            print("Unable to send mail.")
            # logger.error(e)
            user.delete()
            return Response({'alert_error': str (e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

        # return Response({'alert_success': 'Enviamos um link para redefinir sua senha'}, status=status.HTTP_200_OK)
        add = {'alert_success': '%-' + user_data['username'] + '-% foi criado com sucesso'}
        data = json.loads(json.dumps(user_data, cls=DjangoJSONEncoder))
        data.update(add)
        return Response(data, status=status.HTTP_201_CREATED)


class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSerializer
    token_param_config = openapi.Parameter('token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response({'alert_success': 'Ativado com sucesso'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'alert_error': 'Ativação expirada'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'alert_error': 'Token inválido'}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    def post(self, request):
        if not is_valid_email (request.data['email']):
            request.data['email'] = request.data['email']+'@paravalidar.com'

        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = request.data.copy()
        data['user'] = serializer.data['id']
        userLogin = UserLoginSerializer(data = data)
        if userLogin.is_valid(raise_exception=True):
            userLogin.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class MeAPIView(generics.GenericAPIView):
    serializer_class = MeSerializer
    def get(self, request):
        serializer = self.serializer_class(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangePasswordMobileAPIView(generics.GenericAPIView):
    def post(self, request):
        phone = request.data['mobile']
        user = User.objects.get(mobile=phone)
        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(phone).encode())  # Generating Key
        OTP = pyotp.HOTP(key)  # HOTP Model
        if OTP.verify(request.data["otp"], user.counter): # Verifying the OTP
            user.set_password(request.data['password'])
            user.save()
            return Response({'alert_success': 'Senha Resetada com sucesso!'}, status=202)
        return Response({'alert_error': 'OTP errado ou experado!'}, status=tatus.HTTP_400_BAD_REQUEST)
        

class ChangePasswordEmailAPIView(generics.GenericAPIView):
    def post(self, request):
        user = auth.authenticate(email=request.data['email'], password=request.data['password'])
        if not user:
            return Response({'alert_error': 'Senha autual esta errada!'}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(request.data['passwordNova']) < 8:
            return Response({'alert_error': 'Senha deve ter no minimo 8 caracteres!'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.get(id=user.id)
        user.set_password(request.data['passwordNova'])
        user.save()
        return Response({'alert_success': 'Senha alterada com sucesso!'}, status=202)


class LoginsAPIView(generics.GenericAPIView):
    def get(self, request):
        userLogin = UserLogin.objects.filter(user = request.user).order_by('data', '-hora')
        userLogins = UserLoginSerializer(userLogin, many=True)
        return Response(userLogins.data, status=status.HTTP_200_OK)


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        nome = str(str(request.META['HTTP_ORIGIN']).split('.')[0].upper()).split('/')[-1]
       
        serializer = self.serializer_class(data=request.data)

        email = request.data.get('email', '')

        if User.objects.filter(email=email).exists():

            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=request).domain
            
            relativeLink = reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
            
            redirect_url = request.data.get('redirect_url', '')
            try:
                absurl = '\n' + request.META['HTTP_ORIGIN'] + '/#/resetpassword' + relativeLink
            except:
                absurl = '\n http:mws.mytech.co.mz/#/resetpassword' + relativeLink

            tipoEntidade = TipoEntidade.objects.get(nome=str(nome).capitalize())
     
            logo = 'logo'
      

            email_body =  absurl+ "?redirect_url=" + redirect_url


            html_message = loader.render_to_string(
                'email_reset.html',
                {
                    'link':email_body,
                    'username':user.username,
                    'logo': logo
                }
            )
            
            email_subject = 'Restaurar senha'
            to_list = [email]
            try:

                mail = EmailMultiAlternatives(
                    subject=email_subject,
                    body='Clique no link para restaurar sua senha',
                    to=to_list,
                )
                mail.attach_alternative(html_message, "text/html")
                mail.send() 
            except Exception as e:
                print(e, end="\n")
                return Response({'alert_error': str (e)}, status=500)

        return Response({'alert_success': 'Enviamos um link para redefinir sua senha'}, status=status.HTTP_200_OK)


class Mail (generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def get(self, request):
        nome = 'email' #str(str(request.META['HTTP_ORIGIN']).split('.')[0].upper()).split('/')[-1]
       
        serializer = self.serializer_class(data=request.data)

        email = request.query_params.get('email', 'metanochava@gmail.com')
    

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=request).domain
            
            relativeLink = reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
            
            redirect_url = request.data.get('redirect_url', '')
            try:
                absurl = '\n' + request.META['HTTP_ORIGIN'] + '/#/resetpassword' + relativeLink
            except:
                absurl = '\n http:mws.mytech.co.mz/#/resetpassword' + relativeLink

            logo = 'logo'

            email_body =  absurl+ "?redirect_url=" + redirect_url

            html_message = loader.render_to_string(
                'email_template_reset.html',
                {
                    'link':email_body,
                    'username':user.username,
                    'logo': logo
                }
            )

            
            email_subject = 'Restaurar senha'
            to_list = [email]
            try:

                mail = EmailMultiAlternatives(
                    subject=email_subject,
                    body='Clique no link para restaurar sua senha',
                    to=to_list,
                )
                mail.attach_alternative(html_message, "text/html")
                mail.send() 
            except Exception as e:
                print(e, end="\n")
                return Response({'error - ': str (e)}, status=500)

            
            try:
                sender_email = "noreplay@mytech.co.mz"
                receiver_email = email
                password = "noreplaygmail"

                # Create the MIME object
                message = MIMEMultipart()
                message["From"] = sender_email
                message["To"] = receiver_email
                message["Subject"] = email_subject

                # Attach the body of the email
                body = html_message
                message.attach(MIMEText(body, "html"))

                with smtplib.SMTP_SSL('whost02.whost.co.mz', 465) as server:
                    server.login(sender_email, password)
                    server.sendmail(sender_email, receiver_email, message.as_string())
                    server.quit()
                    
                
                send_mail(
                    subject='Assunto de Teste',
                    message='Olá, este é um e-mail de teste enviado via Django!',
                    from_email='noreplay@mytech.co.mz',
                    recipient_list=['metanochava@gmail.com'],
                    fail_silently=True,
                )

            except Exception as e:
                print(e, end="\n")
                print("Unable to send mail.")
                return Response({'error': str (e)}, status=500)
                # logger.error(e)
                # logger.error("Unable to send mail.")
                pass

        return Response({'alert_success': 'Enviamos um link para redefinir sua senha'}, status=status.HTTP_200_OK)


class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):

        redirect_url = request.GET.get('redirect_url')

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                if len(redirect_url) > 3:
                    return CustomRedirect(redirect_url+'?token_valid=False')
                else:
                    return CustomRedirect(os.environ.get('FRONTEND_URL', '')+'?token_valid=False')

            if redirect_url and len(redirect_url) > 3:
                return CustomRedirect(redirect_url+'?token_valid=True&message=Credentials Valid&uidb64='+uidb64+'&token='+token)
            else:
                return CustomRedirect(os.environ.get('FRONTEND_URL', '')+'?token_valid=False')

        except DjangoUnicodeDecodeError as identifier:
            try:
                if not PasswordResetTokenGenerator().check_token(user):
                    return CustomRedirect(redirect_url+'?token_valid=False')
                    
            except UnboundLocalError as e:
                return Response({'alert_error': 'O token não é válido, solicite um novo'}, status=status.HTTP_400_BAD_REQUEST)



class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'alert_success': True, 'message': 'Senha redefinida com sucesso'}, status=status.HTTP_200_OK)


class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
