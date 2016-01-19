from __future__ import unicode_literals

import json
from django.core.exceptions import ImproperlyConfigured

from django.http import HttpResponse

__all__ = ['AjaxFormMixin']


class AjaxFormMixin(object):
    """
    A mixin that provides a way to show and handle a form in a request.
    """
    response_class = HttpResponse
    initial_data = {}
    form_class = {
        'GET': None,
        'POST': None,
        'PUT': None,
        'DELETE': None,
        'PATCH': None,
    }
    order_by = ''
    success_url = None

    def get_initial_data(self):
        """
        Returns the initial_data data to use for forms on this view.
        """
        return self.initial_data.copy()

    def get_form_class(self):
        """
        Returns the form class to use in this view
        """
        return self.form_class[self.request.method]

    def get_form(self, form_class):
        """
        Returns an instance of the form to be used in this view.
        """
        if form_class:
            return form_class(**self.get_form_kwargs())

        return None

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instancing the form.
        """
        kwargs = {'initial': self.get_initial_data()}
        if self.request.method in ('POST', 'PUT', 'PATCH'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        else:
            kwargs.update({
                'data': self.request.GET,
            })

        return kwargs

    def get_context_data(self, **kwargs):
        return kwargs

    def get_success_url(self):
        if self.success_url:
            url = self.success_url
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a success_url.")
        return url

    def form_invalid(self, form):
        errors = []
        for field, error in form.errors.iteritems():
            errors.append(field)

        return self.error_response('Error in fields: ' + ', '.join(errors))

    def error_response(self, msg, **kwargs):
        kwargs['content_type'] = 'application/json'
        kwargs['status'] = 400

        context = {
            'success': False,
            'general_message': msg,
            'status': 400
        }

        return self.response_class(
            json.dumps(context),
            **kwargs
        )

    def filter_query(self, filter_form):
        raise NotImplementedError

    def order_query(self):
        self.queryset = self.queryset.order_by(self.order_by)
