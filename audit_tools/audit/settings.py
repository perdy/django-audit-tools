from __future__ import unicode_literals

try:
    from django.conf import settings
    DEBUG = settings.DEBUG
except (ImportError, AttributeError):
    settings = None

from audit_tools.audit.db import mongodb_connect

# Blacklisted URLs.
# Each App may have a tuple of regex patterns. For each App, if an URL match a pattern will not be logged.
# Use empty string key for global blacklist.
# Example: { 'api': (r'^/api/.*', r'^/API/.*'), '': (r'global_pattern', ) }
BLACKLIST = getattr(settings, 'AUDIT_BLACKLIST', {})

# Celery queue name
CELERY_QUEUE = getattr(settings, 'AUDIT_CELERY_QUEUE', 'audit')

# Save traces async
RUN_ASYNC = getattr(settings, 'AUDIT_RUN_ASYNC', False)

# Function that returns custom data for each application
CUSTOM_PROVIDER = getattr(settings, 'AUDIT_CUSTOM_PROVIDER', {'audit': 'audit.middleware.custom_provider'})

# List of models that will be logged for audit
LOGGED_MODELS = getattr(settings, 'AUDIT_LOGGED_MODELS', ())

# Activate or deactivate logging
ACTIVATE = getattr(settings, 'AUDIT_ACTIVATE', False)

# Database alias
DB_ALIAS = getattr(settings, 'AUDIT_DB_ALIAS', 'audit')

# Database connection
DB_CONNECTION = getattr(settings, 'AUDIT_DB_CONNECTION',
                        {'HOST': 'localhost', 'PORT': 27017, 'NAME': 'audit', 'USER': '', 'PASSWORD': ''})

# Translate URLs
TRANSLATE_URLS = getattr(settings, 'AUDIT_TRANSLATE_URLS', False)

# Additional indexes for the accesses.
ACCESS_INDEXES = getattr(settings, 'AUDIT_ACCESS_INDEXES', [])

# Additional indexes for the processes.
PROCESS_INDEXES = getattr(settings, 'AUDIT_PROCESS_INDEXES', [])

# Additional indexes for the model actions.
MODEL_ACTION_INDEXES = getattr(settings, 'AUDIT_MODEL_ACTION_INDEXES', [])

if ACTIVATE:
    # Create connection to database
    mongodb_connect(connection=DB_CONNECTION, alias=DB_ALIAS)
