from __future__ import unicode_literals

from rest_framework.response import Response
from rest_framework_mongoengine.serializers import DocumentSerializer
from rest_framework import serializers, pagination

from audit_tools.audit.models import Process, Access, ModelAction


class CurrentPageField(serializers.Field):
    """
    Field that returns the current page.
    """
    page_field = 'page'

    def to_native(self, value):
        return value.number


class CurrentPageSerializer(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'page': self.page.number,
            'count': self.page.paginator.count,
            'results': data
        })


class ProcessSerializer(DocumentSerializer):
    class Meta:
        model = Process
        depth = 1


class AccessSerializer(DocumentSerializer):
    class Meta:
        model = Access
        depth = 5


class ModelActionSerializer(DocumentSerializer):
    class Meta:
        model = ModelAction
        depth = 5
