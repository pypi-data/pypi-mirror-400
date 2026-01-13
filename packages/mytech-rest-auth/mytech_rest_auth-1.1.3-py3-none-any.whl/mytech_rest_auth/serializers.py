from rest_framework import serializers
from .classes.FullPath import FullPath
from .models import *
from drf_writable_nested import WritableNestedModelSerializer
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.exceptions import AuthenticationFailed
from django.core.validators import validate_email

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.db.models import Q





def authenticate(value=None, password=None):
    User = get_user_model()
    try:
        user = User.objects.get(
            Q(mobile=value) | Q(email=value) | Q(username=value)
        )
    except User.DoesNotExist:
        return None
    if user.check_password(password):
        return user
   
    return None

class InputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Input
        fields = ['id', 'nome']
        
class StringSerializer(serializers.ModelSerializer):
    class Meta:
        model = String
        fields = ['id', 'texto']

class UserLoginSerializer( serializers.ModelSerializer):
    class Meta:
        model = UserLogin
        fields = ['id', 'user', 'info', 'dispositivo', 'local_lat','local_lon', 'local_nome','data', 'hora', 'is_blocked']


class RegisterSerializer(serializers.ModelSerializer):

    default_error_messages = {
        'username': 'The username should only contain alphanumeric characters'}

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password', 'mobile')
        

    def validate(self, attrs):
        email = attrs.get('email', '')
        username = attrs.get('username', '')

        if not username.isalnum():
            raise serializers.ValidationError(
                self.default_error_messages)
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)
    class Meta:
        model = User
        fields = ['token']

class MeSerializer(serializers.ModelSerializer):
    perfil = serializers.SerializerMethodField()
    def get_perfil(self, obj):
        request = self.context.get('request')
        if request is None:
            return None

        return {
            'name': str(obj.perfil.url).split('/')[-1], 
            'url': FullPath.url(request, obj.perfil.url), 
            'ext': str(obj.perfil.url).split('.')[-1]
        }
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'perfil', 'mobile']


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)

    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)
    username = serializers.CharField(
        max_length=255, min_length=3, read_only=True)


    tokens = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'username', 'mobile','tokens']

    def get_tokens(self, obj):
        user = User.objects.get(id=obj['id'])
        return {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access']
        }
    


    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        email = email.replace('+', '')
        email = email.replace("@paravalidar.com", '')
        email = email.strip()
       
        if email.isnumeric():
            user = authenticate(value=email, password=password)
        else:
            user =  authenticate(value=email, password=password)
       

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')

        return {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'mobile': user.mobile,
            'tokens': user.tokens
        }

        return super().validate(attrs)


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('O link de redefinição é inválido', 401)

            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise AuthenticationFailed('O link de redefinição é inválido', 401)
        return super().validate(attrs)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_message = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token') 
        pass


class EntidadeSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    def get_logo(self, object):
        request = self.context.get('request')
        return {'name': str(object.logo).split('/')[-1], 'url': FullPath.url(request, object.logo.name), 'ext': str(object.logo).split('.')[-1]}

    class Meta:
        model = Entidade
        fields = ['id', 'nome', 'logo', 'ipu', 'groups', 'admins', 'modelos', 'display_logo', 'display_qr', 'display_bar',  'tipo_entidade', 'entidade_bancaria',  'disc_space', 'disc_used_space', 'disc_free_space', 'rodape', 'estado', 'created_at', 'updated_at', 'is_deleted']


class EntidadeUserSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    @classmethod
    def get_user(self, object):
        """getter method to add field get_user"""
        pessoa = Pessoa.objects.filter(user__id=object.user.id).first()
        user = User.objects.filter(id=object.user.id).first()
        pessoa = PessoaSerializer(pessoa)
        user = UserSerializer(user)
        return {'pessoa': pessoa.data, 'user': user.data}

    class Meta:
        model = EntidadeUser
        fields = ['id', 'entidade', 'user']


class EntidadeLogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entidade
        fields = ['logo']


class SucursalSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    def get_url( self, object):
        suc = []
        sucursalUserGroups = SucursalGroup.objects.all().filter(sucursal__id=object.id)

        sucursal = Sucursal.objects.get(id=object.id)
        entidade = Entidade.objects.get(id=sucursal.entidade.id)

        return str(entidade.tipo_entidade.id)+'/'+str(sucursal.entidade.id)+'/'+str(sucursal.id)+'/'

    class Meta:
        model = Sucursal
        fields = ['id', 'nome', 'entidade', 'endereco', 'l_latitude', 'l_longetude', 'url']


class IdiomaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Idioma
        fields = ['id', 'nome', 'code', 'estado']





class PermissionSerializer(serializers.ModelSerializer):
    content_type_model = serializers.CharField()
    content_type_app = serializers.CharField()
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type', 'content_type_model', 'content_type_app']


class GrupoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']  # , 'permissions'


class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ['id', 'app_label', 'model']

class TipoEntidadeSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()
    def get_icon( self, object):
        request = self.context.get('request')
        return {'name': str(object.icon).split('/')[-1], 'url': FullPath.url(request, object.icon.name),
                'ext': str(object.icon).split('.')[-1]}

    groups = serializers.SerializerMethodField()
    def get_groups( self, object):
        request = self.context.get('request')
        groups = GrupoSerializer(object.groups.all(), many=True)
        return groups.data

    class Meta:
        model = TipoEntidade
        fields = ['id', 'nome', 'estado', 'icon','label', 'groups',  'crair_entidade', 'link', 'header', 'menuEsquerdo', 'footer', 'created_at',
                  'created_at_time', 'updated_at', 'updated_at_time', 'is_deleted']
        read_only_fields = ['icon']

class UserSerializer(serializers.ModelSerializer):
    perfil = serializers.SerializerMethodField()
    def get_perfil(self, obj):
        request = self.context.get('request')
        print(obj.perfil)

        if request is None:
            return None
        return {
            'name': str(obj.perfil.url).split('/')[-1], 
            'url': FullPath.url(request, obj.perfil.url), 
            'ext': str(obj.perfil.url).split('.')[-1]
        }
    class Meta:
        model = User
        fields = ['id', 'perfil', 'username', 'email', 'groups', 'is_verified', 'is_active']


class FicheiroSerializer(serializers.ModelSerializer):
    ficheiro = serializers.SerializerMethodField(source='get_ficheiro_value')
    size = serializers.SerializerMethodField(source='get_size__value')

    def get_ficheiro(self, object):
        request_ = None
        return {'name': str(object.ficheiro).split('/')[-1], 'url': FullPath.url(request_, object.ficheiro.name), 'ext': str(object.ficheiro).split('.')[-1], 'size':object.ficheiro.size}

    def get_size(self, object):
        request_ = None
        return object.ficheiro.size

    class Meta:
        model = Ficheiro
        fields =['id', 'ficheiro', 'size', 'modelo', 'estado', 'chamador', 'funcionalidade', 'sucursal', 'entidade', 'created_at', 'updated_at', 'created_at_time', 'updated_at_time', 'is_deleted']


class FicheiroGravarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ficheiro
        fields =['id', 'ficheiro', 'size', 'modelo', 'estado', 'chamador', 'funcionalidade', 'sucursal', 'entidade', 'created_at', 'updated_at', 'created_at_time', 'updated_at_time', 'is_deleted']

