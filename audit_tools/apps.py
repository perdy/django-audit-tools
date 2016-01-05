# -*- coding: utf-8 -*-
"""
Audit Tools app.
"""
from django.apps import AppConfig
from audit_tools.audit.signals import register_models


class AuditToolsApp(AppConfig):
    name = 'audit_tools'
    verbose_name = 'Audit Tools'

    def ready(self):
        # Register all models listed in LOGGED_MODELS
        register_models()
