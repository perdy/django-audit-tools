from __future__ import unicode_literals

from django.views.generic.edit import ProcessFormView

from audit.views.api.mixins import MongoJSONResponseMixin, ModelAjaxFormMixin


class BaseApiView(ModelAjaxFormMixin, ProcessFormView):
    pass


class ApiView(MongoJSONResponseMixin, BaseApiView):
    def get(self, request, *args, **kwargs):
        if 'pk' in kwargs:
            return self.query_response(pk=kwargs['pk'])
        else:
            # There is no arguments for form so no filtering
            if (len(request.GET.keys()) == 2 and 'csrfmiddlewaretoken' in request.GET and 'page' in request.GET) \
                    or (len(request.GET.keys()) == 1 and 'csrfmiddlewaretoken' in request.GET):
                return self.query_response()
            # Filter
            else:
                form_class = self.get_form_class()
                form = self.get_form(form_class)
                if form.is_valid():
                    return self.query_response(filter_form=form)
                else:
                    return self.form_invalid(form)

    def post(self, request, *args, **kwargs):
        return self.error_response('POST method not implemented')

    def put(self, request, *args, **kwargs):
        return self.error_response('PUT method not implemented')


