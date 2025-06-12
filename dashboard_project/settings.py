from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR is the root of your Django project (e.g., C:\panel\Dashboard)
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# It's good practice to get this from an environment variable.
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key')

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
    'main_app', # Your main application
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Root URL configuration for the project
ROOT_URLCONF = 'dashboard_project.urls' # Assuming your project's main urls file is in dashboard_project

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Directory where Django will look for project-level templates
        'DIRS': [os.path.join(BASE_DIR, 'main_app/templates')],
        'APP_DIRS': True, # Tells Django to look for templates in app-specific 'templates' directories
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

WSGI_APPLICATION = 'dashboard_project.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3', # SQLite database file in your project root
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STATIC_URL = 'static/'
# Additional directories to find static files (e.g., project-wide static assets)
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# --- Media Files Configuration ---
# URL for media files (uploaded by users, generated content)
MEDIA_URL = '/media/'
# Absolute path to the directory where uploaded/generated media files will be saved
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
# Get email credentials from environment variables for security
EMAIL_HOST_USER = os.environ.get('MAIL')
EMAIL_HOST_PASSWORD = os.environ.get('MAIL_PASS')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Print statements for debugging email credentials (remove in production)
print("EMAIL_HOST_USER:", EMAIL_HOST_USER)
print("EMAIL_HOST_PASSWORD =", EMAIL_HOST_PASSWORD)

LOGIN_REDIRECT_URL = '/'
