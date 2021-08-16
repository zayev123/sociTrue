"""
Django settings for soci_3_api project.

Generated by 'django-admin startproject' using Django 3.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from rest_framework.settings import api_settings
from datetime import timedelta
from pathlib import Path
import os
import environ
#myEnv = environ.Env()
# myEnv.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-w#-tre%452pmg#6h34bi)gzw22_5)yz274gxvno@wc-31m$-%u'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

#ALLOWED_HOSTS = ['*']
#ALLOWED_HOSTS = ['localhost', '192.168.10.11']
ALLOWED_HOSTS = ['152.228.215.143', 'socializus.eu', 'www.socializus.eu']

AUTH_USER_MODEL = 'soci3LApp.UserInfo'
# Application definition

TIME_INPUT_FORMATS = ('%H:%i',)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'knox',
    'django_filters',
    'channels',
    'soci3LApp',
    'accounts',
    'social_django',
    'chatSoci',
    'corsheaders',
    # 'flutter_web_app',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'corsheaders.middleware.CorsMiddleware'
]

CORS_ORIGIN_ALLOW_ALL = True


ROOT_URLCONF = 'soci_3_api.urls'

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
                'social_django.context_processors.backends',  # <-- Here
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'soci_3_api.wsgi.application'
ASGI_APPLICATION = 'soci_3_api.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [("redis://:" + 'M90A541x516!' + "@127.0.0.1:6379/0")],
        },
    },
}

# '''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'socidb',
        'USER': 'sociadmin',
        'PASSWORD': 'm9o0n5t4y',
        'HOST': 'localhost',
        'PORT': '',
    }
}




# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'knox.auth.TokenAuthentication',
    ),
}

REST_KNOX = {
    'TOKEN_TTL': timedelta(hours=240),
}


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field
STATIC_URL = '/public/static/'
MEDIA_URL = '/public/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'public/media')
STATIC_ROOT = os.path.join(BASE_DIR, 'public/static')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = (
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)


SOCIAL_AUTH_FACEBOOK_KEY = '312586477267704'
SOCIAL_AUTH_FACEBOOK_SECRET = '747153201390a64982bb1ee59c23abb0'

#SOCIAL_AUTH_FACEBOOK_KEY = '535043614173939'
#SOCIAL_AUTH_FACEBOOK_SECRET = '2165a9d4a6f3cf3b424545823666901a'


SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'locale': 'ru_RU',
    'fields': 'id, name, first_name, last_name, picture.width(300).height(300)'
}


SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '338828353379-rgvvfjr0nbhuffbn43na589nm0kto2jj.apps.googleusercontent.com'
#SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '555778579671-mja493e3jt3lb7o10jc0tsvlktpmhsjp.apps.googleusercontent.com'

GOOGLE_WEB_ID = '338828353379-q1441g6pe01b3u0uvi3dmm2ooqtuid56.apps.googleusercontent.com'
#GOOGLE_WEB_ID = '555778579671-579o9pcv63okubmouh38o10teuvrktus.apps.googleusercontent.com'

SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['email', ]

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'social.pipeline.social_auth.associate_by_email',
    'accounts.pipelines.create_custom_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
)

# ----------------------------------------------------------------------------------------------------------------


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'info.log'),
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
    },
    'loggers': {
        'lapview': {  # Use an empty string
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        },
    }
}
