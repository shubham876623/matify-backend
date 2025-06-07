from pathlib import Path
from datetime import timedelta
import os
from corsheaders.defaults import default_headers  # Needed for custom headers

# ──────────────── Razorpay ──────────────── #
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

# ──────────────── Core Settings ──────────────── #
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-e6pi_6@2ts3)&-n$p_z0o2((y(yah-kn*&)gbz#sp8sm%l48ch'
DEBUG = True

ALLOWED_HOSTS = ['api.matify.io', 'localhost', '127.0.0.1']
CSRF_TRUSTED_ORIGINS = [
    "https://api.matify.io",
]

# ──────────────── Installed Apps ──────────────── #
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',

    'matify_api',
]

AUTH_USER_MODEL = 'matify_api.CustomUser'

# ──────────────── Djoser ──────────────── #
DJOSER = {
    "LOGIN_FIELD": "email",
    "SERIALIZERS": {
        "token_create": "matify_api.serializers.CustomTokenCreateSerializer",  # Optional if overridden
    },
}

# ──────────────── JWT Settings ──────────────── #
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=6000),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ──────────────── REST Framework ──────────────── #
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

# ──────────────── CORS Settings ──────────────── #
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "https://app.matify.io",
]
CORS_ALLOW_HEADERS = list(default_headers) + [
    "content-type",
    "authorization",
]

# ──────────────── CSRF + Cookie Settings ──────────────── #
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "None"

# ──────────────── Middleware ──────────────── #
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be first!
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ──────────────── URLs & WSGI ──────────────── #
ROOT_URLCONF = 'matify_backend.urls'
WSGI_APPLICATION = 'matify_backend.wsgi.application'

# ──────────────── Templates ──────────────── #
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ──────────────── Database ──────────────── #
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ──────────────── Password Validators ──────────────── #
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ──────────────── Localization ──────────────── #
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ──────────────── Static Files ──────────────── #
STATIC_URL = 'static/'

# ──────────────── Default Auto Field ──────────────── #
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
