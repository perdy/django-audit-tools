from __future__ import unicode_literals

from rest_framework_mongoengine.serializers import MongoEngineModelSerializer
from rest_framework import serializers, pagination

from ebury_audit.models import Process, Access, ModelAction


class CurrentPageField(serializers.Field):
    """
    Field that returns the current page.
    """
    page_field = 'page'

    def to_native(self, value):
        return value.number


class CurrentPageSerializer(pagination.BasePaginationSerializer):
    page = serializers.Field(source='number')
    num_pages = serializers.Field(source='paginator.num_pages')


class ProcessSerializer(MongoEngineModelSerializer):
    class Meta:
        model = Process
        depth = 1


class AccessSerializer(MongoEngineModelSerializer):
    class Meta:
        model = Access
        depth = 5


class ModelActionSerializer(MongoEngineModelSerializer):
    class Meta:
        model = ModelAction
        depth = 5
