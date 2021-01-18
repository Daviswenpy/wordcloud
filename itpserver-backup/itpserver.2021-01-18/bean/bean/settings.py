# coding:utf-8
"""
User Name: lianpengcheng@skyguard.com.cn
Date Time: 2018-05-17 16:22:35
File Name: settings.py @v1.0
"""
import os
from config import config


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


LOGIN_REDIRECT_URL = '/'
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'l-#fmpjhrtv$ayd_3!j#k#+4nw=+h8o4_5mt#ns&h8cxf0_c+q'


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


# USE DEBUG LOG
USE_DEBUG_LOG = True


ALLOWED_HOSTS = ['*']


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'django_redis',
    # 'django.contrib.sites',
    # 'django.contrib.flatpages',
    'rest_framework',
    # 'duckadmin',
    'itm',
    'cache_manager',
    # 'djcelery',
    # 'caching',
]


INTERNAL_IPS = [
    'skyguard-admin', 'lianpengcheng@skyguard.com.cn', '172.22.118.55', 'lianpengcheng'
]


# APPEND_SLASH = False


# register with rest_framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'itm.authentication.ExpiringTokenAuthentication',
        # 'rest_framework.authentication.BasicAuthentication',
        # 'rest_framework.authentication.TokenAuthentication',
    ),
    'EXCEPTION_HANDLER': 'itm.exceptions.api_exception_handler',
    'APIFUNCS_HANDLER': (
        'itm.apifuncsmiddleware.DeviceIDCheck',
        'itm.apifuncsmiddleware.USDisplayChange',
        'itm.apifuncsmiddleware.JsonFormater',
    ),
    # 'DEFAULT_PARSER_CLASSES': (
    # ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    )
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'itm.apibasicmiddleware.RestrictAdminByIpMiddleware',
    'itm.apibasicmiddleware.WebAppDebugLogMiddleware',
    'itm.apibasicmiddleware.AdminExceptRaiseMiddleware',
]


PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)


ROOT_URLCONF = 'bean.urls'


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


WSGI_APPLICATION = 'bean.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'OPTIONS': {
            'timeout': 5,
        }
    }
}

DJANGO_REDIS_IGNORE_EXCEPTIONS = True
DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True


REDIS_SERVERS = dict(
    cache_server=dict(host=config.CACHE_URL, port=6379, db=1),
)


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        # 'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        "LOCATION": config.CACHE_URL,
        # 'LOCATION': 'unique-snowflake',
        "TIMEOUT": 3600,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 100},
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            # "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
            # 'MAX_ENTRIES': 300,
            # 'CULL_FREQUENCY': 3,
            "SOCKET_CONNECT_TIMEOUT": 0.3,
            "SOCKET_TIMEOUT": 0.3,
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators
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


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/
LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = False

USE_L10N = True

# USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/


UPLOAD = os.path.join(BASE_DIR, 'upload')
DOWNLOAD = os.path.join(BASE_DIR, 'download')


STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')


SESSION_COOKIE_AGE = 60 * 60


# Celery config
import djcelery
djcelery.setup_loader()

# redis://:password@hostname:port/db_number
BROKER_URL = config.BROKER_URL
CELERY_RESULT_BACKEND = config.BROKER_URL

CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

from kombu import Queue
from kombu.common import Broadcast
QUEUE_BOR = (
    Broadcast('broadcast_tasks'),
    Queue('broadcast_tasks'),
)

CELERY_QUEUES = {
    # "ers_task": {
    #     "exchange": "ers_task",
    #     "exchange_type": "direct",
    #     "routing_key": "ers_task"
    # },
    # "ars_task": {
    #     "exchange": "ars_task",
    #     "exchange_type": "direct",
    #     "routing_key": "ars_task"
    # },
    "mrs_task": {
        "exchange": "mrs_task",
        "exchange_type": "direct",
        "routing_key": "mrs_task"
    },
    "upload_file": {
        "exchange": "upload_file",
        "exchange_type": "direct",
        "routing_key": "upload_file"
    },
}


CELERY_ROUTES = {
    # 'ers_task': {'queue': 'ers_task', "routing_key": 'ers_task'},
    'mrs_task': {'queue': 'mrs_task', "routing_key": 'mrs_task'},
    # 'ars_task': {'queue': 'ars_task', "routing_key": 'ars_task'},
    'upload_file': {'queue': 'upload_file', "routing_key": 'upload_file'},
}


# Logging config
# LOG_PATH = os.path.join(BASE_DIR, 'logs')
LOG_PATH1 = "/var/log/itp/itpserver/logs/"
# if not os.path.isdir(LOG_PATH):
#     os.mkdir(LOG_PATH)
if not os.path.isdir(LOG_PATH1):
    os.makedirs(LOG_PATH1)



DEBUG_FILTERS = ['require_debug_true']

if USE_DEBUG_LOG:
    DEBUG_FILTERS = []


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s PID:%(process)d TID:%(thread)d %(filename)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s PID:%(process)d %(module)s %(funcName)s %(lineno)d %(message)s'
        },
        'short': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'debug_app': {
            'level': 'DEBUG',
            'filters': DEBUG_FILTERS,
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'simple',
            'filename': os.path.join(LOG_PATH1, 'itm_debug.log'),
            'when': 'midnight',
            'backupCount': 7
        },
        # 'filelog': {
        #     'level': 'ERROR',
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'formatter': 'simple',
        #     'filename': os.path.join(LOG_PATH.rstrip('/'), 'itm_error.log'),
        #     'maxBytes': 1024 * 1024 * 5,
        #     'backupCount': 2
        # },
        'filelog': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'simple',
            'filename': os.path.join(LOG_PATH1.rstrip('/'), 'itm_error.log'),
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 7
        }
    },
    'loggers': {
        'django.server': {
            'handlers': ['mail_admins'],
            'propagate': True,
            'level': 'CRITICAL',
        },
        # 'django.request': {
        #     'handlers': ['console', 'debug_app'],
        #     'propagate': True,
        #     'level': 'CRITICAL',
        # },
        'itm.itm': {
            # 'handlers': ['console', 'filelog', 'debug_app', 'filelog1'],
            'handlers': ['console', 'filelog', 'debug_app'],
            'propagate': True,
            'level': 'INFO',
        },
        'itm.apibasicmiddleware': {
            # 'handlers': ['console', 'filelog', 'debug_app', 'filelog1'],
            'handlers': ['console', 'filelog', 'debug_app'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'itm.exceptions': {
            # 'handlers': ['console', 'filelog', 'debug_app', 'filelog1'],
            'handlers': ['console', 'filelog', 'debug_app'],
            'propagate': True,
            'level': 'WARNING',
        },
    }
}


# Email Bankend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = False
EMAIL_HOST = 'smtp.skyguardmis.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'ci-build@skyguardmis.com'
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = 'ci-build@skyguardmis.com'
