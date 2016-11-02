"""
Django settings for read project.

Generated by 'django-admin startproject' using Django 1.9.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'wqu(q!hn%1we=&48qm@qigap_(t#+hq1ljxda-3w+k)#uh!&j0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap3',
    #'nocaptcha_recaptcha',
    'read',
    'library',
    'review',
    'dashboard',
    'edit',
    'search'
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
#pip install yet_another_django_profiler and uncomment below then read https://pypi.python.org/pypi/yet-another-django-profiler/ for use
#    'yet_another_django_profiler.middleware.ProfilerMiddleware',
]

ROOT_URLCONF = 'read.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ os.path.join(BASE_DIR, 'templates'), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "library.context_processors.language_form_context_processor",
            ],
            'libraries' : {
                'read_tags': 'read.templatetags',
            },
        },
    },
]

WSGI_APPLICATION = 'read.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/
LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale"),
]

LANGUAGE_CODE = 'en'
from django.utils.translation import ugettext_lazy as _
LANGUAGES = [
        ('bg', _('Bulgarian')),
        ('hr', _('Croatian')),
        ('cs', _('Czech')),
        ('da', _('Danish')),
        ('nl', _('Dutch')),
        ('en', _('English')),
        ('et', _('Estonian')),
        ('fi', _('Finnish')),
        ('fr', _('French')),
        ('de', _('German')),
        ('el', _('Greek')),
        ('hu', _('Hungarian')),
        ('ga', _('Irish')),
        ('it', _('Italian')),
        ('lv', _('Latvian')),
        ('lt', _('Lithuanian')),
#       ('mt', _('Maltese')), NO MALTESE IN DJANGO
        ('pl', _('Polish')),
        ('pt', _('Portuguese')),
        ('ro', _('Romanian')),
        ('sk', _('Slovak')),
        ('sl', _('Slovenian')),
        ('es', _('Spanish')),
        ('sv', _('Swedish')),
];

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_ROOT = 'static'

STATIC_URL = '/static/'

STATICFILES_DIRS = [

]

#TODO for when use is heavier use memcached
#Enable cache
#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#        'LOCATION': '127.0.0.1:11211',
#    }
#}
#and cache session
#SESSION_ENGINE = "django.contrib.sessions.backends.cache"

# This assumes per app view for these... may promote this sttuff to their own app...??
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
#UseCDNS for libs or static versions
PAGE_SIZE_DEFAULT = 5
USE_CDNS = True
CDNS = {'bootstrap_css' : {'local': "/static/css/bootstrap.min.css", 'cdn' : "//maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" },
       'bootstrap_js' : {'local': "/static/js/bootstrap.min.js", 'cdn' : "//maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"},
       'datatables_css' : {'local': "/static/css/jquery.dataTables.min.css", 'cdn': "//cdn.datatables.net/1.10.12/css/jquery.dataTables.min.css"},
       'datatables_js' : {'local': "/static/js/jquery.dataTables.min.js", 'cdn': "//cdn.datatables.net/1.10.12/js/jquery.dataTables.min.js"},
       'jquery' : {'local' : "/static/js/jquery.js", 'cdn': "//code.jquery.com/jquery-1.12.3.js" },
       'jquery_ui' : {'local' : "/static/js/jquery-ui.min.js", 'cdn': "//code.jquery.com/ui/1.12.1/jquery-ui.min.js" },
       'jquery_ui_css' : {'local' : "/static/css/jquery-ui.css", 'cdn' : "//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css" },
       'chart_js' : {'local': "/static/js/Chart.bundle.min.js", 'cdn': "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.3.0/Chart.bundle.min.js"},

      }

## Auth backend that logs in to transkribus.eu and extends the django.contrib.auth.User
AUTHENTICATION_BACKENDS = [
    'read.backends.TranskribusBackend',
#    'django.contrib.auth.backends.ModelBackend',
]

### parameters for services
#transkribus rest service
TRP_URL = 'https://transkribus.eu/TrpServer/rest/'

PROFILE_LOG_BASE = '/tmp/'
