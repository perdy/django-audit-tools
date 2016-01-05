from __future__ import unicode_literals

"""Audit URLs"""

from django.conf.urls import url, include

from audit_tools.audit.utils import i18n_url

_ = i18n_url

urlpatterns = [
    '',
    url(_(r'^search/'), include('audit_tools.audit.urls.search')),
    url(_(r'^api/'), include('audit_tools.audit.urls.api')),
]
