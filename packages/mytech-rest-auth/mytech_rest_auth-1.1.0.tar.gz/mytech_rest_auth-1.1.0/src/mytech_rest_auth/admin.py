from django.contrib import admin
from django.contrib.auth.models import Permission
from .models import *


admin.site.site_title = 'Auth'
admin.site.index_title = 'Mytech Auth Rest'


class FicheiroAdmin(admin.ModelAdmin):
    list_display = ['id', 'ficheiro', 'modelo', 'funcionalidade']
    list_display_links = ('id',)
    fields =['id', 'ficheiro', 'size', 'modelo', 'estado', 'chamador', 'funcionalidade', 'sucursal', 'entidade', 'created_at', 'updated_at', 'created_at_time', 'updated_at_time', 'is_deleted']
admin.site.register(Ficheiro, FicheiroAdmin)

class PermissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'codename', 'content_type']
    list_display_links = ('id',)
    search_fields = ['id', 'name']
admin.site.register(Permission, PermissionAdmin)

class FrontEndAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome', 'fek', 'fep', 'rule', 'created_at', 'updated_at', 'created_at_time', 'updated_at_time', 'is_deleted']
admin.site.register(FrontEnd, FrontEndAdmin)


class IdiomaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome',  'code' ]
    list_display_links = ('id', )
    search_fields = ['id',  'nome' ]
admin.site.register(Idioma, IdiomaAdmin)


class TipoEntidadeAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome', 'icon', 'created_at', 'updated_at', 'is_deleted']
    list_display_links = ('id', 'nome',)
    search_fields = ['nome']
admin.site.register(TipoEntidade, TipoEntidadeAdmin)


class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'mobile','is_verified_mobile', 'counter', 'email', 'perfil', 'language', 'is_verified', 'is_active', 'is_staff', 'updated_at', 'auth_provider', 'created_at']
    list_display_links = ('id', 'username', 'email')
    search_fields = ['username', 'mobile', 'email', 'nome', 'nome_meio', 'apelido']
admin.site.register(User, UserAdmin)

class UserLoginAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'dispositivo', 'info', 'mobile', 'local_nome', 'local_lat', 'local_lon', 'data', 'hora', 'is_blocked']
    list_display_links = ('id', )
    search_fields = ['local_nome', 'dispositivo', 'user' ]
admin.site.register(UserLogin, UserLoginAdmin)

class EntidadeAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome', 'logo', 'ipu', 'admin_list', 'display_logo', 'display_qr', 'display_bar',  'tipo_entidade', 'entidade_bancaria', 'disc_space', 'disc_used_space', 'disc_free_space', 'rodape', 'estado', 'created_at', 'updated_at', 'is_deleted']
    list_display_links = ('id', 'nome',)
    search_fields = ['nome']

    def admin_list(self, obj):
        return ", ".join(
            [u.username for u in obj.admins.all()]
        )
    admin_list.short_description = "admins"
admin.site.register(Entidade, EntidadeAdmin)

class EntidadeUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'entidade', 'created_at', 'updated_at', 'is_deleted']
    list_display_links = ('id', 'user',)
    search_fields = ['user']
admin.site.register(EntidadeUser, EntidadeUserAdmin)

class SucursalAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome',  'created_at', 'updated_at', 'is_deleted']
    list_display_links = ('id', 'nome',)
    search_fields = ['nome']
admin.site.register(Sucursal, SucursalAdmin)

class SucursalGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'sucursal', 'group', 'created_at', 'updated_at', 'is_deleted']
    list_display_links = ('id', 'sucursal',  'group',)
    search_fields = ['sucursal', 'group']
admin.site.register(SucursalGroup, SucursalGroupAdmin)

class SucursalUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'sucursal', 'user', 'created_at', 'updated_at', 'is_deleted']
    list_display_links = ('id', 'sucursal',  'user',)
    search_fields = ['sucursal', 'user']
admin.site.register(SucursalUser, SucursalUserAdmin)

class SucursalUserGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'sucursal', 'user', 'group', 'created_at', 'updated_at', 'is_deleted']
    list_display_links = ('id', 'sucursal',  'user','group', )
    search_fields = ['sucursal', 'user', 'group']
admin.site.register(SucursalUserGroup, SucursalUserGroupAdmin)