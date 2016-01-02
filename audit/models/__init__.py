"""Audit models"""

from audit.models.process import Process
from audit.models.access import Access
from audit.models.model_action import ModelAction, ACTIONS
from audit.models.models_factory import create_access, update_access, create_model_action
from audit.signals import register_models

# Add compatibility with Generic Views
Process._meta.app_label = 'audit'
Process._meta.object_name = 'Process'
Access._meta.app_label = 'audit'
Access._meta.object_name = 'Access'
ModelAction._meta.app_label = 'audit'
ModelAction._meta.object_name = 'ModelAction'

# Register all models listed in LOGGED_MODELS
register_models()
