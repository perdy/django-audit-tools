"""Ebury Audit models"""

from audit.models.process import *
from audit.models.access import *
from audit.models.model_action import *

# Add compatibility with Generic Views
Process._meta.app_label = 'audit'
Process._meta.object_name = 'Process'
Access._meta.app_label = 'audit'
Access._meta.object_name = 'Access'
ModelAction._meta.app_label = 'audit'
ModelAction._meta.object_name = 'ModelAction'

