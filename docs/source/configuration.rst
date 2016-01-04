:tocdepth: 2

=============
Configuration
=============

To configure Ebury Audit you need to follow the next steps:

#. Add *ebury_audit* to your **INSTALLED_APPS** settings like this::

    INSTALLED_APPS = (
        ...
        'ebury_audit',
    )

#. Add *ebury_audit.middleware.AuditMiddleware* to your **MIDDLEWARE_CLASSES** settings like this::

    MIDDLEWARE_CLASSES = (
        ...
        'ebury_audit.middleware.AuditMiddleware',
    )

#. Configure blacklisted URLs in **EBURY_AUDIT_BLACKLIST** settings.
#. Register models that will be logged in **EBURY_AUDIT_LOGGED_MODELS** settings.
#. Execute the next django command::

    python manage.py prepare_ebury_audit

Settings
========

EBURY_AUDIT_ACTIVATE
--------------------

Activate or deactivate audit.

Default::

    EBURY_AUDIT_ACTIVATE = False 

EBURY_AUDIT_DB_ALIAS
--------------------

MongoDB connection alias.

Default::

    EBURY_AUDIT_DB_ALIAS = 'ebury_audit'

EBURY_AUDIT_DB_CONNECTION
-------------------------

MongoDB connection parameters.

Default::

    EBURY_AUDIT_DB_CONNECTION = {
        'HOST': 'localhost',
        'PORT': 27017,
        'NAME': 'ebury_audit',
        'USER': '',
        'PASSWORD': '',
    }

EBURY_AUDIT_RUN_ASYNC
---------------------

Use Celery to run in async mode.

**Important: Celery concurrency level must be configure to 1 (--concurrency=1 parameter in celeryd start)**

Default::

    EBURY_AUDIT_RUN_ASYNC = False

EBURY_AUDIT_CELERY_QUEUE
------------------------

Celery queue name.

Default::

    EBURY_AUDIT_CELERY_QUEUE = 'ebury_audit'

EBURY_AUDIT_LOGGED_MODELS
-------------------------

List of models that will be logged for audit. Each entry consists in a string that represents a model using *"<module>.<model>"* format.

Example::

    EBURY_AUDIT_LOGGED_MODELS = (
        'ebury_audit.models.Access',
    )

Default::

    EBURY_AUDIT_LOGGED_MODELS = ()

EBURY_AUDIT_BLACKLIST
---------------------

Blacklisted URLs. Each application may have a tuple of regex patterns. If an URL matches a pattern will not be logged. Use empty string key for match in all applications.

Example::

    EBURY_AUDIT_BLACKLIST = {
        'api': (
            r'^/api/',
            r'^/API/',
        )
        '': (
            r'global_pattern',
        )
    }

Default::

    EBURY_AUDIT_BLACKLIST = {}

EBURY_AUDIT_CUSTOM_PROVIDER
---------------------------

Custom data provider. Each application may add custom data to Access entries using own functions.

Default::

    EBURY_AUDIT_CUSTOM_PROVIDER = {
        'ebury_audit': 'ebury_audit.middleware.custom_provider',
    }

EBURY_AUDIT_LOGGING
-------------------

Activate logs for Ebury Audit.

Default::

    EBURY_AUDIT_LOGGING = True

EBURY_AUDIT_LOGGING_PATH
------------------------

Path where logs will be stored.

Default::

    EBURY_AUDIT_LOGGING_PATH = settings.SITE_ROOT or ''

EBURY_AUDIT_TRANSLATE_URLS
--------------------------

Translate ebury-audit URLs:

Default::

    EBURY_AUDIT_TRANSLATE_URLS = False

