import os
from mysite.settings_common import *

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

DEBUG = False

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True

ALLOWED_HOSTS = ['django01.obs.unige.ch', '127.0.0.1', 'testserver']

EMAIL_HOST_PASSWORD = os.environ['DJANGO_EMAIL_PASSWORD'] #cspwhr^U&k8QasR+'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': os.path.join(BASE_DIR, '../initialize_database/server_root.cnf'),
        }
    }
}

MEDIA_ROOT  = os.path.join(BASE_DIR,'../FILES')

# Specific for the server
FORCE_SCRIPT_NAME = '/Research/twin_lenses'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/Research/twin_lenses/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]    

LOGIN_URL = '/Research/twin_lenses/login/'
LOGIN_REDIRECT_URL = '/Research/twin_lenses/'

LOGOUT_URL = '/Research/twin_lenses/login/'
LOGOUT_REDIRECT_URL = '/Research/twin_lenses/login/'

