import os
import sys

from django.core.exceptions import ImproperlyConfigured


def get_env_var(var_name, default=None):
    try:
        return os.environ.get(var_name, default)
    except KeyError:
        error_msg = "Set the %s environment variable" % var_name
        raise ImproperlyConfigured(error_msg)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SECRET_KEY = 't-6l_vxz$j=2@@0a19p*5!6qvw4)=#ggqo5r*9ziz2-8c2%kw$'

ALLOWED_HOSTS = ['*', ]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

PROJECT_APPS = [
    'apps.core',
    'apps.users',
    'apps.food',
    'apps.recipes',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'drf_yasg',
    'django_filters',
    'taggit',
    'searchableselect',

]

INSTALLED_APPS = INSTALLED_APPS + THIRD_PARTY_APPS + PROJECT_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.core.mixins.RequestLogMiddleWare'
]
ROOT_URLCONF = 'calorie.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'calorie.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

#AUTH_USER_MODEL = 'users.User'

REST_FRAMEWORK = {
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DATETIME_FORMAT': '%Y-%m-%d %Z %H:%M:%S.%f',
    'EXCEPTION_HANDLER': 'apps.core.mixins.custom_exception_handler'
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_env_var('DB_NAME'),
        'USER': get_env_var('DB_USER'),
        'PASSWORD': get_env_var('DB_PASSWORD'),
        'HOST': get_env_var('DB_HOST'),
        'PORT': get_env_var('DB_PORT'),
    }
}

SWAGGER_SETTINGS = {
    'LOGIN_URL': 'rest_framework:login',
    'LOGOUT_URL': 'rest_framework:logout',
    'USE_SESSION_AUTH': True,
    'APIS_SORTER': 'alpha',
    'SHOW_REQUEST_HEADERS': True,
    'DOC_EXPANSION': 'none',
    'JSON_EDITOR': True,
    'SECURITY_DEFINITIONS': {
        'api_key': {
            'type': 'apiKey',
            'name': 'jwt',
            'in': 'header',
        },
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.sendgrid.net.'
EMAIL_HOST_USER = 'deltateam'
EMAIL_HOST_PASSWORD = '12345678A'
EMAIL_PORT = 587

BROKER_URL = 'amqp://guest:guest@localhost:5672'

TESTING = sys.argv[1:2] == ['test']

SENDER_EMAIL = 'levon2111@gmail.com'

CELERY_BROKER_URL = 'redis://localhost'
