import os  # Add this import
from pathlib import Path  # Add this import

# Define BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent

# Add a SECRET_KEY
SECRET_KEY = 'django-insecure-4x!@#example$%^&*random_generated_key'

INSTALLED_APPS = [
    'django.contrib.admin',  # Add this line for the admin app
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # ...existing apps...
    'content_tool',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # Required for admin
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Required for admin
    'django.contrib.messages.middleware.MessageMiddleware',  # Required for admin
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # Add paths to custom templates if needed
        'APP_DIRS': True,  # Required for admin templates
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # Required for admin
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DEBUG = True  # Ensure this is set to True for development

ALLOWED_HOSTS = ['*']  # Allow all hosts for development purposes

ROOT_URLCONF = 'web_tool.urls'  # Add this line to specify the URL configuration module

STATIC_URL = '/static/'  # Add this line to configure the base URL for static files

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Use SQLite as the database engine
        'NAME': BASE_DIR / 'db.sqlite3',  # Database file location
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'  # Add this line to configure the default auto field

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'content_tool': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
