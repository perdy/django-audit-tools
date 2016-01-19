# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from unittest import TestCase

from mock import MagicMock, call, patch

from audit_tools.audit.views import ModelActionViewSet


@patch.object(ModelActionViewSet, 'queryset')
class ModelActionViewSetTestCase(TestCase):
    def setUp(self):
        self.ma = ModelActionViewSet()

    def test_filter_date_without_from_neither_to(self, queryset_mock):
        self.ma._filter_date()

        self.assertEqual(queryset_mock.filter.call_count, 0)

    def test_filter_date_with_from(self, queryset_mock):
        date_from = datetime.datetime(2016, 1, 19, 21, 4)

        self.ma._filter_date(date_from=date_from)

        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(queryset_mock.filter.call_args, call(timestamp__gte=date_from))

    def test_filter_date_with_to(self, queryset_mock):
        date_to = datetime.datetime(2016, 1, 19, 21, 4)

        self.ma._filter_date(date_to=date_to)

        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(queryset_mock.filter.call_args, call(timestamp__lte=date_to))

    def test_filter_date_with_from_and_to(self, queryset_mock):
        date_from = datetime.datetime(2016, 1, 19, 21, 4)
        date_to = datetime.datetime(2016, 1, 19, 21, 4)

        self.ma._filter_date(date_from=date_from, date_to=date_to)

        expected_calls = [call(timestamp__gte=date_from), call(timestamp__lte=date_to)]
        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(queryset_mock.filter.call_args, expected_calls[0])
        # Be careful with nested .filter()
        self.assertEqual(queryset_mock.filter().filter.call_count, 1)
        self.assertEqual(queryset_mock.filter().filter.call_args, expected_calls[1])

    def test_filter_model_with_app(self, queryset_mock):
        model_app = 'foo'

        self.ma._filter_model(model_app=model_app)

        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(queryset_mock.filter.call_args, call(model__app=model_app))

    def test_filter_model_with_name(self, queryset_mock):
        model_name = 'foo'

        self.ma._filter_model(model_name=model_name)

        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(queryset_mock.filter.call_args, call(model__name=model_name))

    def test_filter_model_with_instance_id(self, queryset_mock):
        instance_id = 'id'

        self.ma._filter_model(instance_id=instance_id)

        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(queryset_mock.filter.call_args, call(instance__id=instance_id))

    def test_filter_model_with_app_name_and_instance_id(self, queryset_mock):
        model_app = 'foo'
        model_name = 'bar'
        instance_id = 'id'

        self.ma._filter_model(model_app=model_app, model_name=model_name, instance_id=instance_id)

        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(queryset_mock.filter.call_args, call(model__app=model_app))
        self.assertEqual(queryset_mock.filter().filter.call_count, 1)
        self.assertEqual(queryset_mock.filter().filter.call_args, call(model__name=model_name))
        self.assertEqual(queryset_mock.filter().filter().filter.call_count, 1)
        self.assertEqual(queryset_mock.filter().filter().filter.call_args, call(instance__id=instance_id))

    def test_filter_model_without_params(self, queryset_mock):
        self.ma._filter_model()

        self.assertEqual(queryset_mock.filter.call_count, 0)

    @patch('audit_tools.audit.views.api.model_action.Access')
    def test_filter_model_with_date_from(self, access_mock, queryset_mock):
        accesses = ['foo', 'bar']
        filtered_accesses_mock = MagicMock(return_value=accesses)
        access_mock.objects.all().filter = filtered_accesses_mock
        date_from = datetime.datetime(2016, 1, 19, 21, 30)

        self.ma._filter_by_accesses(date_from=date_from)

        self.assertEqual(filtered_accesses_mock.call_count, 1)
        self.assertEqual(filtered_accesses_mock.call_args, call(time__request__gte=date_from))
        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(queryset_mock.filter.call_args, call(access__in=accesses))

    @patch('audit_tools.audit.views.api.model_action.Access')
    def test_filter_model_with_date_to(self, access_mock, queryset_mock):
        accesses = ['foo', 'bar']
        filtered_accesses_mock = MagicMock(return_value=accesses)
        access_mock.objects.all().filter = filtered_accesses_mock
        date_to = datetime.datetime(2016, 1, 19, 21, 30)

        self.ma._filter_by_accesses(date_to=date_to)

        self.assertEqual(filtered_accesses_mock.call_count, 1)
        self.assertEqual(filtered_accesses_mock.call_args, call(time__request__lte=date_to))
        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(queryset_mock.filter.call_args, call(access__in=accesses))

    @patch('audit_tools.audit.views.api.model_action.Access')
    def test_filter_model_with_user_id(self, access_mock, queryset_mock):
        accesses = ['foo', 'bar']
        filtered_accesses_mock = MagicMock(return_value=accesses)
        access_mock.objects.all().filter = filtered_accesses_mock
        user_id = 'id'

        self.ma._filter_by_accesses(user_id=user_id)

        self.assertEqual(filtered_accesses_mock.call_count, 1)
        self.assertEqual(filtered_accesses_mock.call_args, call(user__id=user_id))
        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(queryset_mock.filter.call_args, call(access__in=accesses))

    @patch('audit_tools.audit.views.api.model_action.Access')
    def test_filter_model_with_url(self, access_mock, queryset_mock):
        accesses = ['foo', 'bar']
        filtered_accesses_mock = MagicMock(return_value=accesses)
        access_mock.objects.all().filter = filtered_accesses_mock
        url = 'http://www.foo.bar'

        self.ma._filter_by_accesses(url=url)

        self.assertEqual(filtered_accesses_mock.call_count, 1)
        self.assertEqual(filtered_accesses_mock.call_args, call(request__path__icontains=url))
        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(queryset_mock.filter.call_args, call(access__in=accesses))

    @patch('audit_tools.audit.views.api.model_action.Access')
    def test_filter_model_with_view_app(self, access_mock, queryset_mock):
        accesses = ['foo', 'bar']
        filtered_accesses_mock = MagicMock(return_value=accesses)
        access_mock.objects.all().filter = filtered_accesses_mock
        view_app = 'foo'

        self.ma._filter_by_accesses(view_app=view_app)

        self.assertEqual(filtered_accesses_mock.call_count, 1)
        self.assertEqual(filtered_accesses_mock.call_args, call(view__app=view_app))
        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(queryset_mock.filter.call_args, call(access__in=accesses))

    @patch('audit_tools.audit.views.api.model_action.Access')
    def test_filter_model_with_view_name(self, access_mock, queryset_mock):
        accesses = ['foo', 'bar']
        filtered_accesses_mock = MagicMock(return_value=accesses)
        access_mock.objects.all().filter = filtered_accesses_mock
        view_name = 'foo'

        self.ma._filter_by_accesses(view_name=view_name)

        self.assertEqual(filtered_accesses_mock.call_count, 1)
        self.assertEqual(filtered_accesses_mock.call_args, call(view__name=view_name))
        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(queryset_mock.filter.call_args, call(access__in=accesses))

    @patch('audit_tools.audit.views.api.model_action.Access')
    def test_filter_model_with_interlink_id(self, access_mock, queryset_mock):
        accesses = ['foo', 'bar']
        filtered_accesses_mock = MagicMock(return_value=accesses)
        access_mock.objects.all().filter = filtered_accesses_mock
        interlink_id = 'id'

        self.ma._filter_by_accesses(interlink_id=interlink_id)

        self.assertEqual(filtered_accesses_mock.call_count, 1)
        self.assertEqual(filtered_accesses_mock.call_args, call(interlink_id=interlink_id))
        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(queryset_mock.filter.call_args, call(access__in=accesses))

    @patch('audit_tools.audit.views.api.model_action.Access')
    def test_filter_by_accesses_without_params(self, access_mock, queryset_mock):
        self.ma._filter_by_accesses()

        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(access_mock.objects.all().filter.call_count, 0)

    @patch('audit_tools.audit.views.api.model_action.Process')
    def test_filter_by_processes_with_interlink_id(self, process_mock, queryset_mock):
        processes = ['foo', 'bar']
        filtered_processes_mock = MagicMock(return_value=processes)
        process_mock.objects.all().filter = filtered_processes_mock
        interlink_id = 'foobar'

        self.ma._filter_by_processes(interlink_id=interlink_id)

        self.assertEqual(filtered_processes_mock.call_count, 1)
        self.assertEqual(filtered_processes_mock.call_args, call(interlink_id=interlink_id))
        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(queryset_mock.filter.call_args, call(process__in=processes))

    @patch('audit_tools.audit.views.api.model_action.Process')
    def test_filter_by_processes_without_interlink_id(self, process_mock, queryset_mock):
        self.ma._filter_by_processes()

        self.assertEqual(queryset_mock.filter.call_count, 1)
        self.assertEqual(process_mock.objects.all().filter.call_count, 0)

    def test_filter_query(self, queryset_mock):
        filter_form = MagicMock()
        with patch.object(ModelActionViewSet, '_filter_date') as date_mock,\
                patch.object(ModelActionViewSet, '_filter_model') as model_mock, \
                patch.object(ModelActionViewSet, '_filter_by_accesses') as accesses_mock,\
                patch.object(ModelActionViewSet, '_filter_by_processes') as processes_mock:
            self.ma.filter_query(filter_form=filter_form)

        # Check that all data is extracted from form
        expected_calls_form = ['date_from', 'date_to', 'model_app', 'model_name', 'instance_id', 'user_id',
                               'url', 'method_app', 'method_name', 'interlink_access', 'interlink_process']
        calls_form = [i[0][0] for i in filter_form.cleaned_data.get.call_args_list]
        self.assertListEqual(expected_calls_form, calls_form)

        # Check that all filters was applied
        self.assertEqual(date_mock.call_count, 1)
        self.assertEqual(model_mock.call_count, 1)
        self.assertEqual(accesses_mock.call_count, 1)
        self.assertEqual(processes_mock.call_count, 1)

    def tearDown(self):
        pass
