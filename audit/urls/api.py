from __future__ import unicode_literals

from django.conf.urls import url, patterns, include
from rest_framework_mongoengine.routers import MongoDefaultRouter

from audit.views.api import AccessViewSet, ProcessViewSet, ModelActionViewSet

router = MongoDefaultRouter()
router.register(r'access', AccessViewSet)
router.register(r'model_action', ModelActionViewSet)
router.register(r'process', ProcessViewSet)

urlpatterns = patterns(
    '',
    url(r'^', include(router.urls)),
)
