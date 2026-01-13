import json

from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status

from .classes.FullPath import FullPath
from .classes.Translate import Translate
from .models import FrontEnd
from django.conf import settings


class CoreMidlleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        template = str(request.META['PATH_INFO']).split('/')[1]
        if not (template in settings.AUTH_URL):
            if str(request.headers.get('FEK')) != 'None' and str(request.headers.get('FEP')) != 'None':
                if not FrontEnd.objects.filter(fek=str(request.headers.get('FEK')), fep=str(request.headers.get('FEP'))).first():
                    txt = "code 10001 " + Translate.st(request.META['QUERY_STRING'], 'Nao autorizado Bad Credentials') + " " +  request.META['REMOTE_ADDR'] +" "+str(request.headers.get('FEK')) +" "+str(request.headers.get('FEP'))
                    return HttpResponse(txt, status=status.HTTP_401_UNAUTHORIZED, content_type='application/json')
            else:
                if request.META['REMOTE_ADDR'] not in settings.ALLOWED_HOSTS:
                    txt = "code 10002 " + Translate.st(request.META['QUERY_STRING'], 'Nao autorizado No Credentials') + " " + request.META['REMOTE_ADDR']
                    return HttpResponse(txt, status=status.HTTP_401_UNAUTHORIZED, content_type='application/json')

        response = self.get_response(request)
        return response

class CoreFileMidlleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):

        txt = Translate.st(request.META['QUERY_STRING'], 'Nao autorizado')
        qs = request.META['QUERY_STRING']
        path = request.META['PATH_INFO'].split('/')[1]
        token = None

        if path == settings.MEDIA_URL.split('/')[1]:
            if str(qs).__contains__('='):
                if str(qs).__contains__('&'):
                    lang = qs.split('&')
                    for l in lang:
                        if l.split('=')[0] == 'token':
                            token = l.split('=')[1]
                else:
                    if qs.split('=')[0] == 'token':
                        token = qs.split('=')[1]
            if token:
                if FullPath.get_key_file_url_token(token) == settings.URL_FILE_KEY:
                    response = self.get_response(request)
                    return response
            return HttpResponse(txt, status=status.HTTP_401_UNAUTHORIZED, content_type='application/json')
        response = self.get_response(request)
        return response
