import os

DEBUG = True
USE_TZ = True
SECRET_KEY = 'secret_key'
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:"
    }
}
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "audit_tools",
]
MIDDLEWARE_CLASSES = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.SessionAuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    'audit_tools.audit.middleware.AuditMiddleware',
]
SITE_ID = 1
AUDIT_ACTIVATE = True
AUDIT_RUN_ASYNC = False
AUDIT_CELERY_QUEUE = 'audit'
AUDIT_LOGGED_MODELS = ()
AUDIT_BLACKLIST = {
    'demo': (
        r'^(?!(/access/|/modelaction/)).*$',
    )
}
AUDIT_CUSTOM_PROVIDER = {}
AUDIT_DB_ALIAS = 'audit'
AUDIT_DB_CONNECTION = {
    'HOST': '127.0.0.1',
    'NAME': 'audit',
    'USER': os.environ.get('DB_AUDIT_USER'),
    'PASSWORD': os.environ.get('DB_AUDIT_PASSWORD'),
}
