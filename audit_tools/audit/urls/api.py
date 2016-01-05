from __future__ import unicode_literals

from django.conf.urls import url, include
from rest_framework_mongoengine.routers import DefaultRouter as MongoDefaultRouter

from audit_tools.audit.views.api import AccessViewSet, ProcessViewSet, ModelActionViewSet

router = MongoDefaultRouter()
router.register(r'access', AccessViewSet, base_name='access')
router.register(r'model_action', ModelActionViewSet, base_name='model_action')
router.register(r'process', ProcessViewSet, base_name='process')

urlpatterns = [
    '',
    url(r'^', include(router.urls)),
]
