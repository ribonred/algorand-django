from .base import *


DEBUG = True

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases



STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static/staticfiles')
DATABASES = {
    'default': {
        'ENGINE': DB_ENGINE,
        'NAME': os.getenv('DBNAME'),  # dbname
        'USER': os.getenv('DBUSER'),
        'PASSWORD': os.getenv('DBPASSWORD'),
        'HOST': os.getenv('DBHOST'),
        'PORT': 5432,
    },
}
NODE="https://testnet-algorand.api.purestake.io/ps2"
ALGO_TOKEN="J9ERQ8tsgritjH5WP9kT1rgLOx4z9DdmOJQlxij0"