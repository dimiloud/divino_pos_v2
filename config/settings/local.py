from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Désactiver la sécurité SSL en développement
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Email backend pour développement
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Debug toolbar
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: True,
}

# Cors headers pour développement
CORS_ALLOW_ALL_ORIGINS = True