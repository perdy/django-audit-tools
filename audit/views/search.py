from __future__ import unicode_literals

from django.views.generic import TemplateView


class ModelActionView(TemplateView):
    template_name = 'audit/search/model_action/index.html'
