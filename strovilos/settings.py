"""

Django settings for strovilos project.

"""
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Defaults — all overridden by secret_settings in real deployments
ROOT_DIR = os.path.dirname(BASE_DIR)
DEBUG = True
ALLOWED_HOSTS = []

from .secret_settings import *
from django.utils.translation import gettext_lazy as _

########################################################################################################
######################################## Basic/Custom Settings #########################################
########################################################################################################

# Custom Variables
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

POSTS_PER_PAGE = 10
TITLE_COUNT = 10
DESC_COUNT = 28

# Static files (CSS, JavaScript, Images)
# ROOT paths are set in secret_settings
STATIC_URL = '/static/'
MEDIA_URL = '/media/'




# Application definition

INSTALLED_APPS = [
    'anymail',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
    'grappelli',
    'django.contrib.admin',
    'tinymce',
    'compressor',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'main.middleware.AdminLocaleURLMiddleware',
    'login_failure.middleware.RequestProvider',
]


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
                'main.context_processors.global_settings',
            ],
        },
    },
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

ROOT_URLCONF = 'strovilos.urls'
WSGI_APPLICATION = 'strovilos.wsgi.application'


# Password validation

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


# Cache Settings

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}


# Logging Settings

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(module)s.py:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'file': {
            'level': 'WARN',
            'class': 'logging.FileHandler',
            'filename': os.path.join(ROOT_DIR, 'log/debug.log'),
            'formatter' : 'standard',
        },
        'fail2ban_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(ROOT_DIR, 'log/fail2ban.log'),
            'formatter' : 'standard',
        },
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers':['file'],
            'propagate': True,
            'level':'WARN',
        },
        'django.db.backends': {
            'handlers': ['file'],
            'level': 'WARN',
            'propagate': False,
        },
        'main' : {
            'handlers': ['file'],
            'level' : 'WARN',
        },
        'fail2ban': {
            'handlers': ['fail2ban_file'],
            'level': 'ERROR',
       },
    },
}

# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Athens'

USE_I18N = True

USE_L10N = True

USE_TZ = False

LANGUAGES = (
    ('el', _('Greek')),
    ('en', _('English')),
)
ADMIN_LANGUAGE_CODE = 'el'

########################################################################################################
######################################## Installed Apps Settings #######################################
########################################################################################################

# Compress 
COMPRESS_ENABLED = False if DEBUG else True

COMPRESS_CSS_FILTERS = [
	'compressor.filters.css_default.CssAbsoluteFilter',
	'compressor.filters.cssmin.rCSSMinFilter',
]

# Email Agent Setup

# Uncomment this for testing
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'anymail.backends.sendgrid.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@strovilos.gr'
DEFAULT_TO_EMAIL = 'kgstrovilos@gmail.com'

ANYMAIL = {
    'SENDGRID_API_KEY': SENDGRID_API_KEY,
}

# Grappeli

# Enable this to switch between users in admin
# GRAPPELLI_SWITCH_USER = True
GRAPPELLI_ADMIN_TITLE = 'Επεξεργασία Ιστοσελίδας'

# TinyMCE

TINYMCE_DEFAULT_CONFIG = {
    'language': 'el',
    'height': 500,
    'menubar': False,
    'plugins': 'image link lists paste wordcount anchor hr',
    'toolbar': (
        'undo redo | bold italic underline removeformat | '
        'link anchor | image hr | '
        'bullist numlist | wordcount'
    ),
    'images_upload_url': '/tinymce/upload/',
    'images_upload_credentials': True,
    'image_advtab': True,
    'paste_as_text': False,
    'content_style': 'body { font-family: Georgia, serif; font-size: 16px; }',
}
