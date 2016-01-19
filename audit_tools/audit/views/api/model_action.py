from __future__ import unicode_literals

from audit_tools.audit.models import ModelAction, Access, Process
from audit_tools.audit.models.serializers import ModelActionSerializer
from audit_tools.audit.views.api.base import ApiViewSet
from audit_tools.audit.forms.api import ModelActionFilterForm

__all__ = ['ModelActionViewSet']


class ModelActionViewSet(ApiViewSet):
    form_class = {
        'GET': ModelActionFilterForm,
        'POST': None,
        'PUT': None,
        'DELETE': None,
        'PATCH': None,
    }
    model = ModelAction
    serializer_class = ModelActionSerializer
    paginate_by = 10
    order_by = '-timestamp'

    def _filter_date(self, date_from=None, date_to=None):
        """
        Filter QuerySet using a range of dates.

        :param date_from: If given, a filter excluding previous data will be done.
        :type date_from: :class:`datetime.datetime`
        :param date_to: If given, a filter excluding next data will be done.
        :type date_to: :class:`datetime.datetime`
        :return: QuerySet filtered.
        :rtype: :class:`mongoengine.QuerySet`
        """
        if date_from:
            self.queryset = self.queryset.filter(
                timestamp__gte=date_from,
            )

        if date_to:
            self.queryset = self.queryset.filter(
                timestamp__lte=date_to,
            )

        return self.queryset

    def _filter_model(self, model_app=None, model_name=None, instance_id=None):
        """
        Filter QuerySet using a model data.

        :param model_app: If given, a filter for model app will be done.
        :type model_app: str
        :param model_name: If given, a filter for model name will be done.
        :type model_name: str
        :param instance_id: If given, a filter for instance id will be done.
        :type instance_id: str
        :return: QuerySet filtered.
        :rtype: :class:`mongoengine.QuerySet`
        """
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

    def _filter_by_processes(self, interlink_id=None):
        """
        Filter QuerySet using processes interlink ids.

        :param interlink_id: If given, a filter for processes whose interlink id match will be done.
        :type interlink_id: str
        :return: QuerySet filtered.
        :rtype: :class:`mongoengine.QuerySet`
        """
        processes = Process.objects.all()
        if interlink_id:
            processes = processes.filter(interlink_id=interlink_id)

        self.queryset = self.queryset.filter(process__in=processes)

        return self.queryset

    def _filter_by_accesses(self, user_id=None, url=None, view_app=None, view_name=None, interlink_id=None,
                            date_from=None, date_to=None):
        """
        Filter QuerySet using accesses data.

        :param user_id: If given, a filter for accesses whose user id match will be done.
        :type user_id: int
        :param url: If given, a filter for accesses whose url contains this will be done.
        :type url: str
        :param view_app: If given, a filter for accesses whose view app match will be done.
        :type view_app: str
        :param view_name: If given, a filter for accesses whose view name match will be done.
        :type view_name: str
        :param interlink_id: If given, a filter for accesses whose interlink id match will be done.
        :type interlink_id: str
        :param date_from: If given, a filter for accesses whose time request is greater than this will be done.
        :type date_from: :class:`datetime.datetime`
        :param date_to: If given, a filter for accesses whose time request is lesser than this will be done.
        :type date_to: :class:`datetime.datetime`
        :return: QuerySet filtered.
        :rtype: :class:`mongoengine.QuerySet`
        """
        accesses = Access.objects.all()
        if date_from:
            accesses = accesses.filter(time__request__gte=date_from)

        if date_to:
            accesses = accesses.filter(time__request__lte=date_to)

        if user_id:
            accesses = accesses.filter(user__id=user_id)

        if url:
            accesses = accesses.filter(request__path__icontains=url)

        if view_app:
            accesses = accesses.filter(view__app=view_app)

        if view_name:
            accesses = accesses.filter(view__name=view_name)

        if interlink_id:
            accesses = accesses.filter(interlink_id=interlink_id)

        self.queryset = self.queryset.filter(access__in=accesses)

        return self.queryset

    def filter_query(self, filter_form):
        """
        Filter a QuerySet using a filter form.

        :param filter_form: Form with data to filter QuerySet.
        """
        # Filter by date range
        date_from = filter_form.cleaned_data.get('date_from', None)
        date_to = filter_form.cleaned_data.get('date_to', None)
        self._filter_date(date_from, date_to)

        # Filter by model
        model_app = filter_form.cleaned_data.get('model_app', None)
        model_name = filter_form.cleaned_data.get('model_name', None)
        instance_id = filter_form.cleaned_data.get('instance_id', None)
        self._filter_model(model_app, model_name, instance_id)

        # Filter by user
        user_id = filter_form.cleaned_data.get('user_id', None)
        # Filter by url
        url = filter_form.cleaned_data.get('url', None)
        # Filter by view
        view_app = filter_form.cleaned_data.get('method_app', None)
        view_name = filter_form.cleaned_data.get('method_name', None)
        # Filter by interlink access
        interlink_access = filter_form.cleaned_data.get('interlink_access', None)
        self._filter_by_accesses(user_id, url, view_app, view_name, interlink_access, date_from, date_to)

        # Filter by interlink process
        interlink_process = filter_form.cleaned_data.get('interlink_process', None)
        self._filter_by_processes(interlink_process)
