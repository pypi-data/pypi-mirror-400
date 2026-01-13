import uuid


# Create your models here.
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken


class Input(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=100, null=True)
    class Meta:
        permissions = (
            ("list_input", "Can list input"),
        ) 

    def __str__(self):
        return self.nome


class String(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    texto = models.TextField(null=True, blank=True)
    class Meta:
        permissions = (
            ("list_string", "Can list string"),
        ) 

    def __str__(self):
        return str(self.texto)
    
class InputString(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    input = models.ForeignKey(Input, on_delete=models.CASCADE)
    string = models.ForeignKey(String, on_delete=models.CASCADE)

    class Meta:
        permissions = (
            ("list_input_string", "Can List Input  String"),
        ) 

    def __str__(self):
        return self.input.nome + ' | '+str(self.string.texto)





class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None,  mobile=None,):
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
    perfil = models.ImageField(default='user.png', upload_to=profile_image_path, null=True, blank=True)
    username = models.CharField(max_length=255, unique=False)
    mobile = models.CharField(max_length=55,  null=True, unique=True, blank=True, default=None)
    is_verified_mobile = models.BooleanField(blank=False, default=False)
    counter = models.IntegerField(default=0, blank=False)   # For HOTP Verification
    email = models.EmailField(max_length=255, null=True, unique=True, blank=True, default=None)
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
        verbose_name = "User"
        verbose_name_plural = "Users"
        permissions = (
            ("list_user", "Can list user"),
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
            ("list_userlogin", "Can list user login"),
        )
       
    def __str__(self):
        return  str(self.dispositivo)


def icon_path(instance, file_name):
    return f'{instance.nome}/{file_name}'
class TipoEntidade(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=100, null=True)
    icon = models.FileField(upload_to=icon_path, default='logo.png', blank=True)
    license = models.TextField(default='license')
    label = models.CharField(max_length=100, null=True)
    header= models.TextField(default='bg-grey-2 text-grey-9')
    menuEsquerdo= models.TextField(default='bg-grey-2 text-grey-9')
    footer = models.TextField(default='bg-grey-2 text-grey-9')
    ordem = models.IntegerField(default=2)
    crair_entidade = models.BooleanField(max_length=100, null=True, default=True)

    STATUS = (
        ('Activo', 'Activo'),
        ('Desativado', 'Desativado')
    )

    estado = models.CharField(max_length=100, null=True, choices=STATUS)
    groups = models.ManyToManyField(Group, blank=True)
    modelos = models.ManyToManyField(ContentType, blank=True)
    language = models.CharField(max_length=25, default="PT")
    link= models.CharField(max_length=500, default="link")
    created_at = models.DateField(null=True, auto_now_add=True)
    updated_at = models.DateField(null=True, auto_now=True)
    created_at_time = models.DateField(null=True, auto_now_add=True)
    updated_at_time = models.DateField(null=True, auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("list_tipoentidade", "Can list tipo entidade"),
        )
    def __str__(self):
        return self.nome


class Modulo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    icon = models.ImageField(upload_to='icon', default='logo.png', blank=True)
    nome = models.CharField(max_length=100, null=True)
    STATUS = (
        ('Activo', 'Activo'),
        ('Desativado', 'Desativado')
    )
    estado = models.CharField(max_length=100, null=True, choices=STATUS)
    created_at = models.DateField(null=True, auto_now_add=True)
    updated_at = models.DateField(null=True, auto_now=True)
    created_at_time = models.DateField(null=True, auto_now_add=True)
    updated_at_time = models.DateField(null=True, auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("list_modulo", "Can list modulo"),
        )

    def __str__(self):
        return  self.nome

class FrontEnd(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=100, null=True)
    fek = models.CharField(max_length=300, null=True)
    fep = models.CharField(max_length=300, null=True)
    STATUS = (
        ('Read', 'Read'),
        ('Write', 'write'),
        ('ReadWrite','ReadWrite')
    )
    rule = models.CharField(max_length=100, null=True, choices=STATUS)
    created_at = models.DateField(null=True, auto_now_add=True)
    updated_at = models.DateField(null=True, auto_now=True)
    created_at_time = models.TimeField(null=True, auto_now_add=True)
    updated_at_time = models.DateTimeField(null=True, auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("list_front_end", "Can list front end"),
        )

    def __str__(self):
        return  self.nome

def logo_path(instance, file_name):
    return f'{instance.tipo_entidade.nome}/{instance.nome}/{file_name}'
class Entidade(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=100, null=True, default='-')
    logo = models.FileField(upload_to=logo_path, default='logo.png', blank=True)
    display_logo = models.BooleanField(default=True, null=True, blank=True)
    display_bar = models.BooleanField(default=True, null=True, blank=True)
    display_qr = models.BooleanField(default=True, null=True, blank=True)
    tipo_entidade = models.ForeignKey(TipoEntidade, on_delete=models.CASCADE)
    entidade_bancaria = models.CharField(max_length=100, null=True, blank=True)
    groups = models.ManyToManyField(Group, blank=True)
    modelos = models.ManyToManyField(ContentType, blank=True)
    admins = models.ManyToManyField(User, blank=False)
    ipu = models.CharField(max_length=500, null=True, blank=True)
    rodape = models.CharField(max_length=2000, null=True)
    disc_space = models.FloatField( default=1048576.0, null=True)
    disc_used_space = models.FloatField(default=0.0, null=True)
    disc_free_space = models.FloatField(default=1048576.0, null=True)

    STATUS = (
        ('Activo', 'Activo'),
        ('Desativado', 'Desativado')
    )
    estado =models.CharField(max_length=100, null=True, default='Desativado', choices=STATUS)
    created_at = models.DateField(null=True, auto_now_add=True)
    updated_at = models.DateField(null=True, auto_now=True)
    created_at_time = models.DateField(null=True, auto_now_add=True)
    updated_at_time = models.DateField(null=True, auto_now=True)
    is_deleted = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        if self.disc_free_space is None or self.disc_free_space > self.disc_space:
            self.disc_free_space = self.disc_space - self.disc_used_space
        super(Entidade, self).save(*args, **kwargs)

    class Meta:
        permissions = (
            ("list_entidade", "Can list entidade"),
        )

    def __str__(self):
        return  self.nome

    
class Sucursal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=100, null=True)
    entidade = models.ForeignKey(Entidade, on_delete=models.CASCADE)
    l_latitude= models.CharField(max_length=100, default='.', null=True)
    l_longetude= models.CharField(max_length=100,  default='.', null=True)
    endereco = models.CharField(max_length=300,  default='.', null=True)
    rodape = models.CharField(max_length=600,  default='.', null=True)
    icon = models.CharField(max_length=100,  default='.', null=True)
    label = models.CharField(max_length=100,  default='.', null=True)
    groups = models.ManyToManyField(Group,  default='.', blank=True)
    STATUS = (
        ('Activo', 'Activo'),
        ('Desativado', 'Desativado')
    )
    estado =models.CharField(max_length=100, default='Desativado', null=True, choices=STATUS)
    created_at = models.DateField(null=True, auto_now_add=True)
    updated_at = models.DateField(null=True, auto_now=True)
    created_at_time = models.DateField(null=True, auto_now_add=True)
    updated_at_time = models.DateField(null=True, auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("list_sucursal", "Can list sucursal"),
        )

    def __str__(self):
        return  self.nome


class Idioma(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=100, null=True)
    code = models.CharField(max_length=100, null=True)
    STATUS = (
        ('Activo', 'Activo'),
        ('Desativado', 'Desativado')
    )
    estado =models.CharField(max_length=100, default='Activo', null=True, choices=STATUS)
    created_at = models.DateField(null=True, auto_now_add=True)
    updated_at = models.DateField(null=True, auto_now=True)
    created_at_time = models.DateField(null=True, auto_now_add=True)
    updated_at_time = models.DateField(null=True, auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("list_idioma", "Can list idioma"),
        )

    def __str__(self):
        return  self.nome


class EntidadeGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entidade = models.ForeignKey(Entidade, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    created_at = models.DateField(null=True, auto_now_add=True)
    updated_at = models.DateField(null=True, auto_now=True)
    created_at_time = models.DateField(null=True, auto_now_add=True)
    updated_at_time = models.DateField(null=True, auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("list_entidadegroup", "Can list entidade group"),
        )
    def __str__(self):
        return str(self.entidade.nome)+ "  |  "+str(self.group.name)


class EntidadeUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entidade = models.ForeignKey(Entidade, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateField(null=True, auto_now_add=True)
    updated_at = models.DateField(null=True, auto_now=True)
    created_at_time = models.DateField(null=True, auto_now_add=True)
    updated_at_time = models.DateField(null=True, auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("list_entidadeuser", "Can list entidade user"),
        )

    def __str__(self):
        return str(self.entidade.nome) + "  |  " + str(self.user.username)


class SucursalGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    created_at = models.DateField(null=True, auto_now_add=True)
    updated_at = models.DateField(null=True, auto_now=True)
    created_at_time = models.DateField(null=True, auto_now_add=True)
    updated_at_time = models.DateField(null=True, auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("list_sucursalgroup", "Can list sucursal group"),
        )
    def __str__(self):
        return str(self.sucursal.nome)+" | "+str(self.group.name)+" "

class SucursalUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateField(null=True, auto_now_add=True)
    updated_at = models.DateField(null=True, auto_now=True)
    created_at_time = models.DateField(null=True, auto_now_add=True)
    updated_at_time = models.DateField(null=True, auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("list_sucursaluser", "Can list sucursal user"),
        )

    def __str__(self):
        return str(self.sucursal.nome)+" | "+str(self.user.username)+" "


class SucursalUserGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    created_at = models.DateField(null=True, auto_now_add=True)
    updated_at = models.DateField(null=True, auto_now=True)
    created_at_time = models.DateField(null=True, auto_now_add=True)
    updated_at_time = models.DateField(null=True, auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("list_sucursalusergroup", "Can list sucursal user group"),
        )

    def __str__(self):
        return str(self.user.username)+ "   |  "+str(self.sucursal.nome)+ "   |  "+str(self.group.name)



class Ficheiro(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ficheiro = models.FileField( upload_to='ficheiros', null=True, blank=True)
    size = models.FloatField(null=False)
    modelo = models.CharField(max_length=100, null=True)    
    STATUS = (
        ('Activo', 'Activo'),
        ('Desativado', 'Desativado')
    )
    estado =models.CharField(max_length=100, null=True, default='Desactivado', choices=STATUS)

    ESCOLHA = (
        ('File', 'File'),
        ('Perfil', 'Perfil'),
        ('Logo', 'Logo'),
        ('Foto', 'Foto'),
        ('CapaSite', 'CapaSite')
    )
    
    funcionalidade =models.CharField(max_length=100, null=True, default='File', choices=ESCOLHA)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, null=True, blank=True)
    entidade = models.ForeignKey(Entidade, on_delete=models.CASCADE, null=True, blank=True)
    chamador = models.CharField(max_length= 100, null=True, blank=True)
    created_at = models.DateField(null=True, auto_now_add=True)
    updated_at = models.DateField(null=True, auto_now=True)
    created_at_time = models.DateField(null=True, auto_now_add=True)
    updated_at_time = models.DateField(null=True, auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        permissions = (
            ("list_ficheiro", "Can list ficheiros"),
        )

    def __str__(self):
        return  self.ficheiro.name
      