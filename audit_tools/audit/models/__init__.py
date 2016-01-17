"""Ebury Audit models"""

from audit_tools.audit.models.access import *
from audit_tools.audit.models.model_action import *
from audit_tools.audit.models.process import *

# Add compatibility with Generic Views
Process._meta.app_label = 'audit'
Process._meta.object_name = 'Process'
Access._meta.app_label = 'audit'
Access._meta.object_name = 'Access'
ModelAction._meta.app_label = 'audit'
ModelAction._meta.object_name = 'ModelAction'

