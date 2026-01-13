from django.contrib.auth.models import Permission, Group
from rest_framework import permissions
from rest_framework import status
from django.conf import settings
from rest_framework.response import Response
from .classes.Translate import Translate
import inspect
from .models import *


def hasPermission(role=None):
    def decorator(view_func):
        def wrapper_func(self, request, *args, **kwargs):
            tipo_entidade_id = request.headers.get('ET')
            entidade_id = request.headers.get('E')
            sucursal_id = request.headers.get('S')
            grupo_id = request.headers.get('G')
            txt = Translate.st(request.query_params.get('lang'), 'Permission denied')
            he_has =False
            
            user = request.user
            # Verifica a role (pode adaptar isso ao seu modelo)
            if len(Entidade.objects.filter(id=entidade_id, tipo_entidade__id=tipo_entidade_id))<=0:
                txt = 'Entidade não esta nesse tipo de entidade'
                txt = Translate.st(request.query_params.get('lang'), txt)
                return Response({'alert_error': txt}, status=status.HTTP_403_FORBIDDEN)
            
            if len(EntidadeUser.objects.filter(user__id=request.user.id, entidade_id=entidade_id))<=0:
                txt = 'User não esta nessa de entidade'
                txt = Translate.st(request.query_params.get('lang'), txt)
                return Response({'alert_error': txt}, status=status.HTTP_403_FORBIDDEN)   
                    
            if len(Sucursal.objects.filter(id=sucursal_id, entidade__tipo_entidade__groups__id=grupo_id))<=0:
                txt = 'Sucursal ou entidade ou Tipo Entidade não tem esse perfil'
                txt = Translate.st(request.query_params.get('lang'), txt)
                return Response({'alert_error': txt}, status=status.HTTP_403_FORBIDDEN)
                        
            if len(SucursalUser.objects.filter(user__id=request.user.id, sucursal__id=sucursal_id))<=0:
                txt = 'Usuario não esta nesta nessa Sucursal'
                txt = Translate.st(request.query_params.get('lang'), txt)
                return Response({'alert_error': txt}, status=status.HTTP_403_FORBIDDEN)

            try:
                re = False
                for p in SucursalUserGroup.objects.filter(sucursal__id=sucursal_id, user__id=request.user.id, group__id=grupo_id):
                    re= True
                if re:
                    grupo = Group.objects.get(id=grupo_id)
                    permissions = grupo.permissions.all()
                    if int(grupo.id) == int(grupo_id):
                        for permission in permissions:
                            if permission.codename in role:
                                he_has = True
            except:
                txt = 'Usuario não tem esse perfil nessa sucursal'
                txt = Translate.st(request.query_params.get('lang'), txt)
                return Response({'alert_error': txt}, status=status.HTTP_403_FORBIDDEN)
                       
            if he_has:
                return view_func(self, request, *args, **kwargs)
            
            txt = Translate.st(request.query_params.get('lang'), txt)
            return Response({'alert_error': txt}, status=status.HTTP_403_FORBIDDEN)
        
        return wrapper_func
    return decorator


def isPermited(role=None, request=None):
    caller = inspect.stack()[1].function
    # print("Fui chamado por:", caller)
    tipo_entidade_id = request.headers.get('ET')
    entidade_id = request.headers.get('E')
    sucursal_id = request.headers.get('S')
    grupo_id = request.headers.get('G')

    # print(entidade_id)
    # print(tipo_entidade_id)
    he_has =False
    
    user = request.user
    if len(Entidade.objects.filter(id=entidade_id, tipo_entidade__id=tipo_entidade_id))<=0:
        return  he_has
    if len(EntidadeUser.objects.filter(user__id=request.user.id, entidade_id=entidade_id))<=0:
        return  he_has        
    if len(Sucursal.objects.filter(id=sucursal_id, entidade__tipo_entidade__groups__id=grupo_id))<=0:
        return  he_has         
    if len(SucursalUser.objects.filter(user__id=request.user.id, sucursal__id=sucursal_id))<=0:
        return  he_has
    try:
        re = False
        for p in SucursalUserGroup.objects.filter(sucursal__id=sucursal_id, user__id=request.user.id, group__id=grupo_id):
            re= True
        if re:
            grupo = Group.objects.get(id=grupo_id)
            permissions = grupo.permissions.all()
            if int(grupo.id) == int(grupo_id):
                for permission in permissions:
                    if permission.codename in role:
                        he_has = True
    except:
        return  he_has   

    return he_has         
        