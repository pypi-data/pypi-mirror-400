from ..models import User

def Create(name):
    try:
        username = User.objects.get(username=name).username
        numero = int("".join(filter(str.isdigit, username)))
        letras = "".join(filter(str.isalpha, s))
        h = numero+1
        username =f'{letras}{h}'
        return Create(username)
    except:
        return name