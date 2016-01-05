from __future__ import unicode_literals

from django.conf.urls import url, patterns
from django.contrib.auth.decorators import permission_required
from audit_tools.audit.utils import i18n_url as _
from audit_tools.audit.views.search import ModelActionView as ModelActionSearchView, AccessView as AccessSearchView


def access_required(view):
    return permission_required('audit.api')(permission_required('audit.search')(view))

urlpatterns = patterns(
    '',
    url(_(r'^model_action/?'), access_required(ModelActionSearchView.as_view()), name='model_action_search'),
    url(_(r'^access/?'), access_required(AccessSearchView.as_view()), name='access_search'),
)
