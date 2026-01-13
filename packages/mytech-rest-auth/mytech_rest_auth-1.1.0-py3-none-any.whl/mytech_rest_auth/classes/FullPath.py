import string
import random
from .Translation import Translation

from django.conf import settings

class FullPath:
    @staticmethod
    def generate_file_url_token():
        characters = string.ascii_letters + string.digits
        code = ''
        translacao = random.choice(string.digits.replace('0', ''))
        encode_key = int(random.choice(string.digits.replace('0', '')))
        code = code.join(translacao)
        chave_encriptada = Translation.encrypt(settings.URL_FILE_KEY, encode_key)

        for i in range(len(chave_encriptada)):
            separacao = ''
            for j in range(int(translacao)):
                separacao = separacao + random.choice(characters)
            code = code + separacao + chave_encriptada[i]

        code = code + str(encode_key)
        return code

    @staticmethod
    def get_key_file_url_token(code):
        try:
            translacao = int(code[0])
        except Exception:
            return ''
        try:
            encode_key = int(code[-1])
        except Exception:
            return ''
            
        chave = ''
        j = 0
        tamanho = (len(code[1:-1]) / translacao)
        for i in range(int(tamanho)):
            j = j + 1
            help = (translacao * j) + j
            try:
                chave = chave + code[1:-1][help - 1]
            except Exception as e:
                pass
        return Translation.decrypt(chave, encode_key)

    @staticmethod
    def url(request, name):
        gerado = FullPath.generate_file_url_token()
        return request.build_absolute_uri(name) +'?token=' + gerado 

    
