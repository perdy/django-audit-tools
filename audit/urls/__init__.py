from __future__ import unicode_literals

"""Audit URLs"""

from django.conf.urls import url, patterns, include

from audit.utils import i18n_url

_ = i18n_url

urlpatterns = patterns(
    '',
    url(_(r'^search/'), include('audit.urls.search')),
    url(_(r'^api/'), include('audit.urls.api')),
)
