from __future__ import unicode_literals

from django.conf.urls import url, patterns
from django.contrib.auth.decorators import permission_required
from audit.utils import i18n_url
from audit.views.search import ModelActionView as ModelActionSearchView

_ = i18n_url

access_api_and_search_required = lambda x: permission_required('audit.api')(permission_required('audit.search')(x))

urlpatterns = patterns(
    '',
    url(_(r'^model_action/'), access_api_and_search_required(ModelActionSearchView.as_view()), name='model_action_search'),
)