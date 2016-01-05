from __future__ import unicode_literals

from django.views.generic import TemplateView

__all__ = ['ModelActionView', 'AccessView']


class ModelActionView(TemplateView):
    template_name = 'audit/search/model_action/index.html'


class AccessView(TemplateView):
    template_name = 'audit/search/access/index.html'
