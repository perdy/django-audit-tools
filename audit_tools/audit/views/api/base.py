from __future__ import unicode_literals

from rest_framework_mongoengine.viewsets import ReadOnlyModelViewSet
from audit_tools.audit.permissions import APIAccess

from audit_tools.audit.views.api.mixins import AjaxFormMixin
from audit_tools.audit.models.serializers import CurrentPageSerializer


class APIViewSet(AjaxFormMixin, ReadOnlyModelViewSet):
    """Base viewset for API views.
    """
    pagination_serializer_class = CurrentPageSerializer
    permission_classes = (APIAccess, )

    def get_queryset(self):
        if not self.queryset:
            self.queryset = self.model.objects.all()

        filter_form = self.get_form(self.get_form_class())
        if filter_form:
            if filter_form.is_valid():
                self.filter_query(filter_form=filter_form)
            else:
                return self.form_invalid(filter_form)

        if self.order_by:
            self.order_query()

        return self.queryset