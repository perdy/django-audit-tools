# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unittest import TestCase

import datetime
from mock import MagicMock, call, patch

from audit_tools.audit.views import AccessViewSet


@patch.object(AccessViewSet, 'queryset')
class AccessViewSetTestCase(TestCase):
    def setUp(self):
        self.access = AccessViewSet()

    def test_filter_date_without_from_neither_to(self, queryset_mock):
        self.access._filter_date()

        self.assertEqual(queryset_mock.filter.call_count, 0)

    def test_filter_date_with_from(self, queryset_mock):
        date_from = datetime.datetime(2016, 1, 18, 21, 4)

        self.access._filter_date(date_from=date_from)

        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(queryset_mock.filter.call_args, call(time__request__gte=date_from))

    def test_filter_date_with_to(self, queryset_mock):
        date_to = datetime.datetime(2016, 1, 18, 22, 5)

        self.access._filter_date(date_to=date_to)

        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(queryset_mock.filter.call_args, call(time__request__lte=date_to))

    def test_filter_date_with_from_and_to(self, queryset_mock):
        date_from = datetime.datetime(2016, 1, 18, 22, 5)
        date_to = datetime.datetime(2016, 1, 18, 22, 5)

        self.access._filter_date(date_from=date_from, date_to=date_to)

        expected_calls = [call(time__request__gte=date_from), call(time__request__lte=date_to)]
        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(queryset_mock.filter.call_args, expected_calls[0])
        # Be careful with nested .filter()
        self.assertEqual(queryset_mock.filter().filter.call_count, 1)
        self.assertEqual(queryset_mock.filter().filter.call_args, expected_calls[1])

    def test_filter_user_with_id(self, queryset_mock):
        user_id = 1

        self.access._filter_user(user_id=user_id)

        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(queryset_mock.filter.call_args, call(user__id=user_id))

    def test_filter_user_without_id(self, queryset_mock):
        self.access._filter_user()

        self.assertEqual(queryset_mock.filter.call_count, 0)

    def test_filter_url_with_url(self, queryset_mock):
        url = 'http://www.foo.bar'

        self.access._filter_url(url=url)

        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(queryset_mock.filter.call_args, call(request__path__icontains=url))

    def test_filter_url_without_url(self, queryset_mock):
        self.access._filter_url()

        self.assertEqual(queryset_mock.filter.call_count, 0)

    def test_filter_view_with_app(self, queryset_mock):
        view_app = 'foo'

        self.access._filter_view(view_app=view_app)

        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(queryset_mock.filter.call_args, call(view__app=view_app))

    def test_filter_view_with_name(self, queryset_mock):
        view_name = 'foo'

        self.access._filter_view(view_name=view_name)

        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(queryset_mock.filter.call_args, call(view__name=view_name))

    def test_filter_view_with_app_and_name(self, queryset_mock):
        view_name = 'foo'
        view_app = 'bar'

        self.access._filter_view(view_name=view_name, view_app=view_app)

        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(queryset_mock.filter.call_args, call(view__app=view_app))
        # Be careful with nested .filter()
        self.assertEqual(queryset_mock.filter().filter.call_count, 1)
        self.assertEqual(queryset_mock.filter().filter.call_args, call(view__name=view_name))

    def test_filter_view_without_app_neither_name(self, queryset_mock):
        self.access._filter_view()

        self.assertEqual(queryset_mock.filter.call_count, 0)

    def test_filter_interlink_with_id(self, queryset_mock):
        interlink_id = 'foo'

        self.access._filter_interlink(interlink_id=interlink_id)

        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(queryset_mock.filter.call_args, call(interlink_id=interlink_id))

    def test_filter_interlink_without_id(self, queryset_mock):
        self.access._filter_interlink()

        self.assertEqual(queryset_mock.filter.call_count, 0)

    @patch('audit_tools.audit.views.api.access.Process')
    def test_filter_by_processes_with_interlink_id(self, process_mock, queryset_mock):
        processes = ['foo', 'bar']
        filtered_processes_mock = MagicMock(return_value=processes)
        process_mock.objects.all().filter = filtered_processes_mock
        interlink_id = 'foobar'

        self.access._filter_by_processes(interlink_id=interlink_id)

        self.assertEqual(filtered_processes_mock.call_count, 1)
        self.assertEqual(filtered_processes_mock.call_args, call(interlink_id=interlink_id))
        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(queryset_mock.filter.call_args, call(process__in=processes))

    @patch('audit_tools.audit.views.api.access.Process')
    def test_filter_by_processes_without_interlink_id(self, process_mock, queryset_mock):
        self.access._filter_by_processes()

        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(process_mock.objects.all().filter.call_count, 0)

    def test_filter_query(self, queryset_mock):
        filter_form = MagicMock()
        with patch.object(AccessViewSet, '_filter_date') as date_mock,\
                patch.object(AccessViewSet, '_filter_user') as user_mock, \
                patch.object(AccessViewSet, '_filter_url') as url_mock, \
                patch.object(AccessViewSet, '_filter_view') as view_mock,\
                patch.object(AccessViewSet, '_filter_interlink') as interlink_mock, \
                patch.object(AccessViewSet, '_filter_by_processes') as processes_mock:
            self.access.filter_query(filter_form=filter_form)

        # Check that all data is extracted from form
        expected_calls_form = ['date_from', 'date_to', 'user_id', 'url', 'method_app', 'method_name',
                               'interlink_access', 'interlink_process']
        calls_form = [i[0][0] for i in filter_form.cleaned_data.get.call_args_list]
        self.assertListEqual(expected_calls_form, calls_form)

        # Check that all filters was applied
        self.assertEqual(date_mock.call_count, 1)
        self.assertEqual(user_mock.call_count, 1)
        self.assertEqual(url_mock.call_count, 1)
        self.assertEqual(view_mock.call_count, 1)
        self.assertEqual(interlink_mock.call_count, 1)
        self.assertEqual(processes_mock.call_count, 1)

    def tearDown(self):
        pass
