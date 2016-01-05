from __future__ import unicode_literals

from functools import wraps
import datetime

from django.shortcuts import render_to_response
from django.utils import timezone
from django.views.generic import TemplateView, View, DetailView
from django.views.generic.base import TemplateResponseMixin

from demo.models import Test
from audit_tools.audit.models import Access, ModelAction
from audit_tools.audit.decorators import DisableAudit


def test_decorator(func):
    @wraps(func)
    def inner(*args, **kwargs):
        return func(*args, **kwargs)
    return inner


class HomeView(TemplateView):
    template_name = 'home.html'


class AccessView(TemplateView):
    template_name = 'access.html'


class AccessExceptionView(TemplateView):
    template_name = 'access.html'

    def get(self, request, *args, **kwargs):
        raise RuntimeError('Intended exception')


def access_function_based_view(request):
    return render_to_response('access.html', {})


@test_decorator
def access_decorated_view(request):
    return render_to_response('access.html', {})


class LastAccessView(DetailView):
    template_name = 'last_access.html'
    context_object_name = 'access'

    def get_object(self, queryset=None):
        try:
            return Access.objects.order_by('-time__request')[0]
        except:
            return None


class LastModelActionView(DetailView):
    template_name = 'last_modelaction.html'
    context_object_name = 'modelaction'

    def get_object(self, queryset=None):
        try:
            return ModelAction.objects.order_by('-timestamp')[0]
        except:
            return None


class CreateModelActionView(TemplateResponseMixin, View):
    template_name = 'create_modelaction.html'

    def create(self, *args, **kwargs):
        self.object = Test(name='test', force_time=datetime.datetime.now().time())
        self.object.save()
        return self.object

    def get(self, request, *args, **kwargs):
        self.create(*args, **kwargs)
        self.request = request
        return self.render_to_response({})

    def post(self, request, *args, **kwargs):
        self.create(*args, **kwargs)
        self.request = request
        return self.render_to_response({})


class UpdateModelActionView(TemplateResponseMixin, View):
    template_name = 'update_modelaction.html'

    def update(self, *args, **kwargs):
        self.object = Test.objects.all().order_by('-pk')[0]
        self.object.name = 'TestUpdated'
        self.object.time = timezone.now()
        self.object.save()
        return self.object

    def get(self, request, *args, **kwargs):
        self.update(*args, **kwargs)
        self.request = request
        return self.render_to_response({})

    def post(self, request, *args, **kwargs):
        self.update(*args, **kwargs)
        self.request = request
        return self.render_to_response({})


class DeleteModelActionView(TemplateResponseMixin, View):
    template_name = 'delete_modelaction.html'

    def delete(self, *args, **kwargs):
        self.object = Test.objects.all().order_by('-pk')[0]
        self.object.delete()
        return self.object

    def get(self, request, *args, **kwargs):
        self.delete(*args, **kwargs)
        self.request = request
        return self.render_to_response({})

    def post(self, request, *args, **kwargs):
        self.delete(*args, **kwargs)
        self.request = request
        return self.render_to_response({})

