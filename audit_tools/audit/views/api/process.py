from __future__ import unicode_literals

from audit_tools.audit.models import Process
from audit_tools.audit.models.serializers import ProcessSerializer
from audit_tools.audit.views.api.base import APIViewSet

__all__ = ['ProcessViewSet']


class ProcessViewSet(APIViewSet):
    form_class = {
        'GET': None,
        'POST': None,
        'PUT': None,
        'DELETE': None,
        'PATCH': None,
    }
    model = Process
    serializer_class = ProcessSerializer
    paginate_by = 10
    order_by = '-creation_time'
