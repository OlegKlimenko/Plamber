# -*- coding: utf-8 -*-

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(BASE_DIR + '/Plamber/settings.json') as file:
    settings = json.loads(file.read())

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = settings['SECRET_KEY']
API_SECRET_KEY = settings['API_SECRET_KEY']
GOOGLE_RECAPTCHA_SECRET_KEY = settings['GOOGLE_RECAPTCHA_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = settings['DEBUG']

ALLOWED_HOSTS = settings['ALLOWED_HOSTS']

CSRF_COOKIE_SECURE = settings['CSRF_COOKIE_SECURE']
SESSION_COOKIE_SECURE = settings['SESSION_COOKIE_SECURE']

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',

    'app',
    'api'
)

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'app.middleware.reminder_middleware.ReminderMiddleware'
)

ROOT_URLCONF = 'Plamber.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'Plamber.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'mysql.connector.django',
        'NAME': settings['DATABASE']['NAME'],
        'USER': settings['DATABASE']['USER'],
        'PASSWORD': settings['DATABASE']['PASSWORD'],
        'HOST': settings['DATABASE']['HOST'],
        'PORT': '3306'
    }
}

# Encrypting

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
]

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[%(levelname)s][%(asctime)s]: %(message)s'
        }
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'test_changes.log' if DEBUG else 'changes.log'),
            'formatter': 'simple'
        }
    },
    'loggers': {
        'changes': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True,
        }
    }
}

# REST framework settings

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}

if DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer'
    )
else:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
        'rest_framework.renderers.JSONRenderer',
    )

# Mail settings

EMAIL_HOST = settings['EMAIL']['HOST']
EMAIL_PORT = settings['EMAIL']['PORT']
EMAIL_HOST_USER = settings['EMAIL']['USER']
EMAIL_HOST_PASSWORD = settings['EMAIL']['PASSWORD']
EMAIL_USE_TLS = True

# Mailgun settings

MAILGUN_DOMAIN = settings['MAILGUN']['DOMAIN']
MAILGUN_API_KEY = settings['MAILGUN']['API_KEY']
MAILGUN_FROM_MAIL = settings['MAILGUN']['FROM']

# Celery settings

CELERY_BROKER_URL = settings['CELERY']['BROKER_URL']
CELERY_RESULT_BACKEND = settings['CELERY']['RESULT_BACKEND']
CELERY_ACCEPT_CONTENT = settings['CELERY']['ACCEPT_CONTENT']
CELERY_TASK_SERIALIZER = settings['CELERY']['TASK_SERIALIZER']
CELERY_RESULT_SERIALIZER = settings['CELERY']['RESULT_SERIALIZER']

# Uploading settings

DATA_UPLOAD_MAX_MEMORY_SIZE = None

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

ADMIN_URL = settings['ADMIN_URL']

# Additional app settings

BOOKS_PER_PAGE = 48
