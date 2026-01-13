# lib
Este e para armazenar librires



# django-cors-headers==4.9.0
## pip install django-cors-headers

### Inside settings.py:

```bash 
    INSTALLED_APPS = [
    'corsheaders',
    ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://84.247.162.222:9000",
]

CORS_ALLOW_CREDENTIALS = True

from corsheaders.defaults import default_headers
CORS_ALLOW_HEADERS = list(default_headers) + [
    "fek",
    "fep",
]


```


dependencies = [
  "Django>=5.2.8",
  "djangorestframework==3.16.1",
  "djangorestframework-simplejwt==5.2.2",
  "rest-framework-simplejwt==0.0.2",
  "drf-writable-nested==0.7.2",
  "drf-yasg==1.21.11",
  "pyotp==2.9.0",
  "pillow==12.0.0",
  "django-cors-headers==4.9.0",
]
