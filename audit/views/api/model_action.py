from __future__ import unicode_literals

from audit.forms import ModelActionFilterForm as ModelActionAjaxForm
from audit.models import ModelAction, Access, Process
from audit.views.api import ApiView


class ModelActionView(ApiView):
    form_class = {
        'GET': ModelActionAjaxForm,
        'POST': None,
        'PUT': None,
        'DELETE': None,
    }
    paginated_by = 10

    def __init__(self):
        super(ModelActionView, self).__init__()
        self.queryset = None

    def _filter_date_gte(self, date_from):
        self.queryset = self.queryset.filter(
            timestamp__gte=date_from,
        )

        return self.queryset

    def _filter_date_lte(self, date_to):
        self.queryset = self.queryset.filter(
            timestamp__lte=date_to,
        )

        return self.queryset

    def _filter_url(self, url, date_from=None, date_to=None):
        accesses = Access.objects.filter(
            request__path=url
        )

        if date_from:
            accesses = accesses.filter(time__request__gte=date_from)

        if date_to:
            accesses = accesses.filter(time__request__lte=date_to)

        self.queryset = self.queryset.filter(
            access__in=accesses
        )

        return self.queryset

    def _filter_user(self, user_id, date_from=None, date_to=None):
        accesses = Access.objects.filter(
            user__id=user_id,
        )

        if date_from:
            accesses = accesses.filter(time__request__gte=date_from)

        if date_to:
            accesses = accesses.filter(time__request__lte=date_to)

        self.queryset = self.queryset.filter(
            access__in=accesses,
        )

        return self.queryset

    def _filter_model(self, model_app=None, model_name=None, instance_id=None):
        if model_app:
            self.queryset = self.queryset.filter(
                model__app=model_app,
            )

        if model_name:
            self.queryset = self.queryset.filter(
                model__name=model_name,
            )

        if instance_id:
            self.queryset = self.queryset.filter(
                instance__id=instance_id,
            )

        return self.queryset

    def _filter_view(self, date_from=None, date_to=None, view_app=None, view_name=None):
        accesses = Access.objects.all()

        if date_from:
            accesses = accesses.filter(time__request__gte=date_from)

        if date_to:
            accesses = accesses.filter(time__request__lte=date_to)

        if view_app:
            accesses = accesses.filter(
                view__app=view_app,
            )

        if view_name:
            accesses = accesses.filter(
                view__name=view_name,
            )

        self.queryset = self.queryset.filter(
            access__in=accesses,
        )

        return self.queryset

    def _filter_interlink(self, date_from=None, date_to=None, interlink_access=None, interlink_process=None):
        if interlink_access:
            accesses = Access.objects.filter(
                interlink_id=interlink_access,
            )

            if date_from:
                accesses = accesses.filter(time__request__gte=date_from)

            if date_to:
                accesses = accesses.filter(time__request__lte=date_to)

            self.queryset = self.queryset.filter(
                access__in=accesses,
            )

        if interlink_process:
            processes = Process.objects.filter(
                interlink_id=interlink_process,
            )

            self.queryset = self.queryset.filter(
                process__in=processes,
            )

        return self.queryset

    def make_query(self, **kwargs):
        form = kwargs.get('filter_form', None)
        pk = kwargs.get('pk', None)

        if pk:
            self.queryset = ModelAction.objects.get(id=pk)
            result = self.queryset
        elif form:
            try:
                self.queryset = ModelAction.objects.all()

                # Filter by date range
                date_from = form.cleaned_data.get('date_from', None)
                date_to = form.cleaned_data.get('date_to', None)
                if date_from:
                    self._filter_date_gte(date_from)

                if date_to:
                    self._filter_date_lte(date_to)

                # Filter by user
                user_id = form.cleaned_data.get('user_id', None)
                if user_id:
                    self._filter_user(user_id, date_from, date_to)

                # Filter by url
                url = form.cleaned_data.get('url', None)
                if url:
                    self._filter_url(url, date_from, date_to)

                # Filter by model
                model_app = form.cleaned_data.get('model_app', None)
                model_name = form.cleaned_data.get('model_name', None)
                instance_id = form.cleaned_data.get('instance_id', None)
                if model_name or model_app or instance_id:
                    self._filter_model(model_app, model_name, instance_id)

                # Filter by view
                view_app = form.cleaned_data.get('method_app', None)
                view_name = form.cleaned_data.get('method_name', None)
                if view_app or view_name:
                    self._filter_view(date_from, date_to, view_app, view_name)

                # Filter by interlink
                interlink_access = form.cleaned_data.get('interlink_access', None)
                interlink_process = form.cleaned_data.get('interlink_process', None)
                if interlink_process or interlink_access:
                    self._filter_interlink(date_from, date_to, interlink_access, interlink_process)

                try:
                    page = self.get_current_page()
                    result = self.get_query_page(page)
                except (KeyError, AttributeError):
                    result = self.queryset
            except KeyError as e:
                raise KeyError('Field {} not found in form'.format(e))
        else:
            self.queryset = ModelAction.objects.all()
            try:
                page = self.get_current_page()
                result = self.get_query_page(page)
            except (KeyError, AttributeError):
                result = self.queryset

        try:
            # Result is a QuerySet
            result = result.order_by('-timestamp')
        except AttributeError:
            pass

        return result