from __future__ import unicode_literals

import json
from django.core.exceptions import ImproperlyConfigured

from django.http import HttpResponse


class MultipleObjectJSONMixin(object):
    page_context_name = 'page'
    num_pages_context_name = 'last'
    paginated_by = 10

    def get_page_context_name(self):
        return self.page_context_name

    def get_num_pages_context_name(self):
        return self.num_pages_context_name

    def get_paginated_by(self):
        return self.paginated_by

    def get_current_page(self):
        context_name = self.get_page_context_name()
        if self.request.method in ('POST', 'PUT'):
            page = int(self.request.POST[context_name])
        elif self.request.method == 'GET':
            page = int(self.request.GET[context_name])
        else:
            raise KeyError("page")

        return page

    def get_num_pages(self):
        try:
            num_pages = self.queryset.count() / self.paginated_by or 1
        except AttributeError:
            num_pages = None

        return num_pages

    def get_query_page(self, page):
        init_range = self.paginated_by * (page - 1)
        end_range = self.paginated_by * page
        return self.queryset[init_range:end_range]


class AjaxFormMixin(object):
    """
    A mixin that provides a way to show and handle a form in a request.
    """

    initial = {}
    form_class = {
        'GET': None,
        'POST': None,
        'PUT': None,
        'DELETE': None,
    }
    success_url = None

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        return self.initial.copy()

    def get_form_class(self):
        """
        Returns the form class to use in this view
        """
        return self.form_class[self.request.method]

    def get_form(self, form_class):
        """
        Returns an instance of the form to be used in this view.
        """
        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instanciating the form.
        """
        kwargs = {'initial': self.get_initial()}
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        elif self.request.method == 'GET':
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

    def query_response(self, **kwargs):
        # Get queries
        query = self.make_query(**kwargs)

        # Make paginator context
        try:
            paginator = {
                self.get_page_context_name(): self.get_current_page(),
                self.get_num_pages_context_name(): self.get_num_pages(),
                'paginated_by': self.get_paginated_by()
            }

            response = {
                'query': query,
                'paginator': paginator
            }
        except (KeyError, AttributeError):
            response = {
                'query': query,
            }

        return self.render_to_response(response)

    def form_invalid(self, form):
        errors = []
        for field, error in form.errors.iteritems():
            errors.append(field)

        return self.error_response('Error in fields: ' + ', '.join(errors))


class ModelAjaxFormMixin(AjaxFormMixin, MultipleObjectJSONMixin):
    pass


class JSONResponseMixin(object):
    """
    A mixin that can be used to render a JSON response.
    """
    response_class = HttpResponse

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        response_kwargs['content_type'] = 'application/json'

        try:
            json_response = self.convert_context_to_json(context)
            return self.response_class(json_response, **response_kwargs)
        except Exception as e:
            return self.error_response(str(e))

    def convert_context_to_json(self, context):
        """
        Convert the context dictionary into a JSON object"
        :param context: Context dictionary
        :return: JSON object
        """
        return json.dumps(context)

    def error_response(self, msg, **kwargs):
        kwargs['content_type'] = 'application/json'
        kwargs['status'] = 400

        context = {
            'sucess': False,
            'general_message': msg,
            'status': 400
        }

        return self.response_class(
            json.dumps(context),
            **kwargs
        )

    def filter_query_get(self, **kwargs):
        """Make QuerySets
        """
        return None


class MongoJSONResponseMixin(MultipleObjectJSONMixin, JSONResponseMixin):
    def convert_context_to_json(self, context):
        try:
            # Dump query
            query = context['query']
            query_str = '"query": ' + query.to_json()

            try:
                # Dump paginator
                paginator = context['paginator']
                paginator_str = '"paginator": ' + json.dumps(paginator)

                # Compose response
                response_str = "{" + paginator_str + ", " + query_str + "}"
            except KeyError:
                response_str = "{" + query_str + "}"

            return response_str
        except AttributeError:
            raise AttributeError('Error parsing query into JSON')
        except KeyError:
            raise AttributeError('Invalid query')
