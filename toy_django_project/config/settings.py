"""
Django settings for django_project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-development-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'


AUTH_USER_MODEL = 'org.User'


ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Application definition

INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'org.apps.OrgConfig',
	'rules_tap',
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [],
		'APP_DIRS': True,
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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# Parse database connection URL
database_url = os.environ.get('DATABASE_URL', '')
parts = database_url.split('://', 1)[1].split('@')
user_pass, host_port_name = parts[0], parts[1]
user, password = user_pass.split(':')
host_port, name = host_port_name.split('/')
host, port = host_port.split(':')

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': name,
		'USER': user,
		'PASSWORD': password,
		'HOST': host,
		'PORT': port,
		'TEST': {
			'NAME':f"{name}_test",
			'USER': user,
			'PASSWORD': password,
			'HOST': host,
			'PORT': port,
		},
	}
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


LOGGING = {
	"version": 1,
	"disable_existing_loggers": False,
	"filters": {
		"require_debug_false": {
			"()": "django.utils.log.RequireDebugFalse",
		},
		"require_debug_true": {
			"()": "django.utils.log.RequireDebugTrue",
		},
	},
	"formatters": {
		"django.server": {
			"()": "django.utils.log.ServerFormatter",
			"format": "[{server_time}] {message}",
			"style": "{",
		}
	},
	"handlers": {
		"console": {
			"level": "INFO",
			"filters": ["require_debug_true"],
			"class": "logging.StreamHandler",
		},
		"django.server": {
			"level": "INFO",
			"class": "logging.StreamHandler",
			"formatter": "django.server",
		},
		"mail_admins": {
			"level": "ERROR",
			"filters": ["require_debug_false"],
			"class": "django.utils.log.AdminEmailHandler",
		},
	},
	"loggers": {
		"django": {
			"handlers": ["console", "mail_admins"],
			"level": "INFO",
		},
		"django.server": {
			"handlers": ["django.server"],
			"level": "INFO",
			"propagate": False,
		},
	},
}



# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField' 

RULES_TAP_CONFIG = {
	'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY'),
	'MODULE_PATHS': ['/app/toy_django_project/org'],
	'FILE_CHUNK_EXCLUDE_PATHS': ['**/admin.py', '**/migrations/**'],
	'WORKDIR': BASE_DIR / 'out',
	'SANDBOX_DB_USER': 'mr_ai',
	'MIGRATIONS_APP_LABEL': 'org',
	'VIEWABLE_DB_TABLES': 'org.sandbox.VIEWABLES_TABLES',
}