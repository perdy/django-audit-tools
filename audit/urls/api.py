from __future__ import unicode_literals

from django.conf.urls import url, patterns
from django.contrib.auth.decorators import permission_required
from audit.views.api import AccessView
from audit.views.api.model_action import ModelActionView
from audit.views.api.process import ProcessView


urlpatterns = patterns(
    '',
    url(r'^model_action/', permission_required('audit.access_api')(ModelActionView.as_view()), name='api_model_action_list'),
    url(r'^model_action/(?P<pk>[\w\d]+)/', permission_required('audit.access_api')(ModelActionView.as_view()), name='api_model_action_single'),
    url(r'^process/(?P<pk>[\w\d]+)/', permission_required('audit.access_api')(ProcessView.as_view()), name='api_process_single'),
    url(r'^access/(?P<pk>[\w\d]+)/', permission_required('audit.access_api')(AccessView.as_view()), name='api_access_single'),
)