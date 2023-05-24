from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

MEDIA_ROOT = BASE_DIR / '../media/'
CORS_ALLOW_ALL_ORIGINS = True
