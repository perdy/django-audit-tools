==================
Django Audit Tools
==================

.. image:: https://travis-ci.org/PeRDy/django-audit-tools.svg?branch=master
    :target: https://travis-ci.org/PeRDy/django-audit-tools
.. image:: https://coveralls.io/repos/PeRDy/django-audit-tools/badge.svg?branch=master&service=github 
    :target: https://coveralls.io/github/PeRDy/django-audit-tools?branch=master
.. image:: https://img.shields.io/pypi/v/django-audit-tools.svg
    :target: https://pypi.python.org/pypi/django-audit-tools/
    :alt: Latest Version
.. image:: https://landscape.io/github/PeRDy/django-audit-tools/master/landscape.svg?style=flat
    :target: https://landscape.io/github/PeRDy/django-audit-tools/master
    :alt: Code Health
    
:Version: 0.3.0
:Status: Development
:Author: José Antonio Perdiguero López

**Warning:** This package is currently under development, use at your own risk.

**Note:** I started the development of this project meanwhile I was working in Ebury_. So I want to show gratitude for release the code to share it with open source community.

Django application that provides a set of tools for auditing requests and models and improve logging.

Full documentation in ReadTheDocs_.

Quick start
===========

#. Add *audit_tools* to your **INSTALLED_APPS** settings like this::

    INSTALLED_APPS = (
        ...
        'audit_tools',
    )

#. Add *audit.middleware.AuditMiddleware* to your **MIDDLEWARE_CLASSES** settings like this::

    MIDDLEWARE_CLASSES = (
        ...
        'audit_tools.audit.middleware.AuditMiddleware',
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

    AUDIT_ACTIVATE = True

AUDIT_DB_ALIAS
--------------

Audit database connection alias.

Default::

    AUDIT_DB_ALIAS = 'audit'

AUDIT_DB_CONNECTION
-------------------

Audit database connection parameters.

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
        'audit_tools.audit.models.Access',
    )

Default::

    AUDIT_LOGGED_MODELS = ()

AUDIT_BLACKLIST
---------------

Blacklisted URLs. Each application may have a tuple of regex patterns. If an URL matches a pattern will not be logged.

Example::

    AUDIT_BLACKLIST = {
        'api': (
            r'^/api/.*',
            r'^/API/.*',
        )
    }

Default::

    AUDIT_BLACKLIST = {}

AUDIT_ACCESS_INDEXES
--------------------

Custom indexes for the accesses. There is the possibility to add new custom indexes to the Audit database.

Example::

    AUDIT_ACCESS_INDEXES = [
        'custom.pools.names',
        'custom.pools.num_polls',
        ('custom.pools.names', 'custom.pools.num_polls'),
    ]



AUDIT_PROCESS_INDEXES
---------------------

Custom indexes for the processes. There is the possibility to add new custom indexes to the Audit database.


AUDIT_MODEL_ACTION_INDEXES
--------------------------

Custom indexes for the model actions. There is the possibility to add new custom indexes to the Audit database.


AUDIT_CUSTOM_PROVIDER
---------------------

Custom data provider. Each application may add custom data to Access entries using own functions.

Default::

    AUDIT_CUSTOM_PROVIDER = {
        'audit_tools': 'audit_tools.audit.middleware.custom_provider',
    }

AUDIT_TRANSLATE_URLS
--------------------

Translate Audit URLs:

Default::

    AUDIT_TRANSLATE_URLS = False

.. _ReadTheDocs: http://django-audit-tools.readthedocs.org/
.. _Ebury: http://www.ebury.com
