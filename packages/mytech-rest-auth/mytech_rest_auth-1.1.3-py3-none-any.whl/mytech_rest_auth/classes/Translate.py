import  os
from csv import DictReader
import re

class Translate:
    @staticmethod
    def st(lang, texto):

        translations = Translate.getTranslations(Translate.getLang(lang))
        returne = ''
        # print(translations)
        for traduce in translations:
            key = str(list(traduce.keys())[0]).strip()
            valor = str(list(traduce.values())[0]).strip()
            if ( Translate.remocao(key) == Translate.remocao(texto)):
                traducao = valor
                returne= Translate.replaceTraducao( texto, traducao)

        if returne == '':
            returne = texto

        return returne

    @staticmethod
    def getTranslations(lang):
        traducao_ = []
        if lang:
            pass
        else:
            lang = "PT-PT"
        try:
            with open(str(os.getcwd()) + '/core/lang/{}.csv'.format(lang), 'r') as read_obj:
                csv_dict_reader = DictReader(read_obj)
                for row in csv_dict_reader:
                    traducao_.append({row['chave']: row['traducao']})
        except Exception as e:
            print(e)
        return traducao_

    @staticmethod
    def remocao(texto):
        newstr = str(texto).replace('/(\s*%-\s*[a-zA-Z-0-9\s*]+\s*-%\s*)/g', ' ')
        return newstr

    @staticmethod
    def captura(texto):
        newstr = texto # str(texto).('/(\s*%-\s*[a-zA-Z-0-9\s*]+\s*-%\s*)/g')
        return newstr

    @staticmethod
    def replaceTraducao(texto, textDeTraducao):
        array = Translate.captura(texto)
        if array != None:
            pass
            # array.forEach(element = > {
            # element = element.replace('%-', '')
            # element = element.replace('-%', '')
            # text = element.trim()
            # co = re.compile('/(\s*%-\s*[a-zA-Z-0-9\s*]+\s*-%\s*)/g')
            # textDeTraducao = textDeTraducao.replace(co, " "+text+" ")
            # })

        return textDeTraducao

    @staticmethod
    def getLang(lang):
        if str(lang).__contains__('='):
            if str(lang).__contains__('&'):
                lang = lang.split('&')
                for l in lang:
                    if l.split('=')[0] == 'lang':
                        return l.split('=')[1]
            else:
                if lang.split('=')[0] == 'lang':
                    return lang.split('=')[1]
        return lang