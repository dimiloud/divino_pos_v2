from .base import *

DEBUG = True

INSTALLED_APPS += ['debug_toolbar']

# Debug toolbar settings
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: True,
}

# Email settings for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}