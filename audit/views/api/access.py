from __future__ import unicode_literals

from audit.forms.api.model_action import ModelActionFilterForm
from audit.models import Access
from audit.views.api import ApiView


class AccessView(ApiView):
    form_class = {
        'GET': ModelActionFilterForm,
        'POST': None,
        'PUT': None,
        'DELETE': None,
    }
    paginated_by = 10

    def make_query(self, **kwargs):
        form = kwargs.get('filter_form', None)
        pk = kwargs.get('pk', None)

        if pk:
            self.queryset = Access.objects.get(id=pk)
            result = self.queryset
        elif form:
            pass
            # TODO: filter using form
            self.queryset = Access.objects.all()
            try:
                page = self.get_current_page()
                result = self.get_query_page(page)
            except (KeyError, AttributeError):
                result = self.queryset
        else:
            self.queryset = Access.objects.all()
            try:
                page = self.get_current_page()
                result = self.get_query_page(page)
            except (KeyError, AttributeError):
                result = self.queryset

        try:
            # Result is a QuerySet
            result = result.order_by('-time__request')
        except AttributeError:
            pass

        return result