import uuid


# Create your models here.
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)

from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken

class PhoneModel(models.Model):
    Mobile = models.IntegerField(blank=False)
    isVerified = models.BooleanField(blank=False, default=False)
    counter = models.IntegerField(default=0, blank=False)   # For HOTP Verification

    def __str__(self):
        return str(self.id)
    
    class Meta:
        permissions = (
            ("icon", "menu"),
            ("list_phonemodel", "Can list phone model"),
        )

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None,  mobile=None,):
        # if username is None:
        #     raise TypeError('Users should have a username')
        # if email is None:
        #     raise TypeError('Users should have a Email')
        # if mobile is None:
        #     mobile ='860000000'
        user = self.model(username=username, email=self.normalize_email(email), mobile=mobile)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password=None):
        if password is None:
            raise TypeError('Password should not be none')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_verified = True
        user.is_staff = True
        user.save()
        return user


AUTH_PROVIDERS = {'facebook': 'facebook', 'google': 'google','twitter': 'twitter', 'email': 'email'}


def profile_image_path(instance, file_name):
    return f'images/users/{instance.id}/{file_name}'

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=255, unique=False)
    mobile = models.CharField(max_length=55,  null=True, unique=True, blank=True, default=None)
    is_verified_mobile = models.BooleanField(blank=False, default=False)
    counter = models.IntegerField(default=0, blank=False)   # For HOTP Verification
    nome = models.CharField(max_length=255, null=True, blank=True)
    nome_meio = models.CharField(max_length=255, null=True, blank=True)
    apelido = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, unique=True, blank=True, default=None)
    perfil = models.ImageField(default='user.png', upload_to=profile_image_path, null=True, blank=True)
    language = models.CharField(max_length=25,default="PT-PT")
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    auth_provider = models.CharField(max_length=255, blank=False,null=False, default=AUTH_PROVIDERS.get('email'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()
    
    def save(self, *args, **kwargs):
        if self.email == '':
            self.email = None
        if self.mobile =='':
            self.mobile = None
        super().save(*args, **kwargs)

    class Meta:
        permissions = (
            ("icon", "menu"),
            ("list_user", "Can List User"),
        )

    def __str__(self):
        return self.username


    def tokens(self):
        refresh =  RefreshToken.for_user(self) 
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }




class UserLogin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dispositivo = models.TextField(null=True)
    mobile = models.CharField(max_length=100,null=True)
    info = models.TextField(null=True)
    local_lat = models.CharField(max_length=100, null=True)
    local_lon = models.CharField(max_length=100, null=True)
    local_nome = models.CharField(max_length=100, null=True)
    data = models.DateField(null=True, auto_now_add=True)
    hora = models.TimeField(null=True, auto_now_add=True)
    is_blocked = models.BooleanField(default= False)

    class Meta:
        permissions = (
            ("icon", "menu"),
            ("list_userlogin", "Can List User Login"),
        )
       
    def __str__(self):
        return  str(self.dispositivo)