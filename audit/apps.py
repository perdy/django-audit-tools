# -*- coding: utf-8 -*-
"""
Audit app.
"""
from django.apps import AppConfig
from audit.signals import register_models


class AuditToolsApp(AppConfig):
    name = 'audit'
    verbose_name = 'Audit Tools'

    def ready(self):
        # Register all models listed in LOGGED_MODELS
        register_models()
