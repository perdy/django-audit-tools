:tocdepth: 2

=============
Configuration
=============

To configure Audit you need to follow the next steps:

#. Add *audit* to your **INSTALLED_APPS** settings like this::

    INSTALLED_APPS = (
        ...
        'audit',
    )

#. Add *audit.middleware.AuditMiddleware* to your **MIDDLEWARE_CLASSES** settings like this::

    MIDDLEWARE_CLASSES = (
        ...
        'audit.middleware.AuditMiddleware',
    )

#. Configure blacklisted URLs in **AUDIT_BLACKLIST** settings.
#. Register models that will be logged in **AUDIT_LOGGED_MODELS** settings.
#. Execute the next django command::

    python manage.py prepare_audit

Settings
========

AUDIT_ACTIVATE
--------------

Activate or deactivate audit.

Default::

    AUDIT_ACTIVATE = False

AUDIT_DB_ALIAS
--------------

MongoDB connection alias.

Default::

    AUDIT_DB_ALIAS = 'audit'

AUDIT_DB_CONNECTION
-------------------

MongoDB connection parameters.

Default::

    AUDIT_DB_CONNECTION = {
        'HOST': 'localhost',
        'PORT': 27017,
        'NAME': 'audit',
        'USER': '',
        'PASSWORD': '',
    }

AUDIT_RUN_ASYNC
---------------

Use Celery to run in async mode.

**Important: Celery concurrency level must be configure to 1 (--concurrency=1 parameter in celeryd start)**

Default::

    AUDIT_RUN_ASYNC = False

AUDIT_CELERY_QUEUE
------------------

Celery queue name.

Default::

    AUDIT_CELERY_QUEUE = 'audit'

AUDIT_LOGGED_MODELS
-------------------

List of models that will be logged for audit. Each entry consists in a string that represents a model using *"<module>.<model>"* format.

Example::

    AUDIT_LOGGED_MODELS = (
        'audit.models.Access',
    )

Default::

    AUDIT_LOGGED_MODELS = ()

AUDIT_BLACKLIST
---------------

Blacklisted URLs. Each application may have a tuple of regex patterns. If an URL matches a pattern will not be logged. Use empty string key for match in all applications.

Example::

    AUDIT_BLACKLIST = {
        'api': (
            r'^/api/',
            r'^/API/',
        )
        '': (
            r'global_pattern',
        )
    }

Default::

    AUDIT_BLACKLIST = {}

AUDIT_CUSTOM_PROVIDER
---------------------

Custom data provider. Each application may add custom data to Access entries using own functions.

Default::

    AUDIT_CUSTOM_PROVIDER = {
        'audit': 'audit.middleware.custom_provider',
    }

AUDIT_LOGGING
-------------

Activate logs for Audit.

Default::

    AUDIT_LOGGING = True

AUDIT_LOGGING_PATH
------------------

Path where logs will be stored.

Default::

    AUDIT_LOGGING_PATH = settings.SITE_ROOT or ''

AUDIT_TRANSLATE_URLS
--------------------

Translate Audit URLs:

Default::

    AUDIT_TRANSLATE_URLS = False

