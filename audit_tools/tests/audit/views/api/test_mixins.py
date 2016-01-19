# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import OrderedDict
from unittest import TestCase

from django.core.exceptions import ImproperlyConfigured
from mock import patch, MagicMock, call

from audit_tools.audit.views.api.mixins import AjaxFormMixin


class AjaxFormMixinTestCase(TestCase):
    def setUp(self):
        self.mixin = AjaxFormMixin()

    @patch.object(AjaxFormMixin, 'initial_data')
    def test_get_initial_data(self, initial_data_mock):
        self.mixin.get_initial_data()

        self.assertEqual(initial_data_mock.copy.call_count, 1)

    def test_get_form_class(self):
        form_class = MagicMock()
        self.mixin.form_class['GET'] = form_class
        request = MagicMock()
        request.method = 'GET'
        self.mixin.request = request

        result = self.mixin.get_form_class()

        self.assertEqual(result, form_class)

    @patch.object(AjaxFormMixin, 'get_form_kwargs', return_value={})
    def test_get_form(self, get_form_kwargs_mock):
        form_class = MagicMock()
        form = MagicMock()
        form_class.return_value = form

        result = self.mixin.get_form(form_class)

        self.assertEqual(form_class.call_count, 1)
        self.assertEqual(result, form)

    def test_get_form_without_class(self):
        result = self.mixin.get_form(None)

        self.assertIsNone(result)

    @patch.object(AjaxFormMixin, 'get_initial_data', return_value={})
    def test_get_form_kwargs_post(self, get_initial_data_mock):
        request = MagicMock()
        request.method = 'POST'
        request.POST = 'foo'
        request.FILES = 'bar'
        self.mixin.request = request

        result = self.mixin.get_form_kwargs()

        self.assertIn('initial', result)
        self.assertIn('data', result)
        self.assertIn('files', result)

    @patch.object(AjaxFormMixin, 'get_initial_data', return_value={})
    def test_get_form_kwargs_put(self, get_initial_data_mock):
        request = MagicMock()
        request.method = 'PUT'
        request.POST = 'foo'
        request.FILES = 'bar'
        self.mixin.request = request

        result = self.mixin.get_form_kwargs()

        self.assertIn('initial', result)
        self.assertIn('data', result)
        self.assertIn('files', result)

    @patch.object(AjaxFormMixin, 'get_initial_data', return_value={})
    def test_get_form_kwargs_patch(self, get_initial_data_mock):
        request = MagicMock()
        request.method = 'PATCH'
        request.POST = 'foo'
        request.FILES = 'bar'
        self.mixin.request = request

        result = self.mixin.get_form_kwargs()

        self.assertIn('initial', result)
        self.assertIn('data', result)
        self.assertIn('files', result)

    @patch.object(AjaxFormMixin, 'get_initial_data', return_value={})
    def test_get_form_kwargs_get(self, get_initial_data_mock):
        request = MagicMock()
        request.method = 'GET'
        request.POST = 'foo'
        request.FILES = 'bar'
        self.mixin.request = request

        result = self.mixin.get_form_kwargs()

        self.assertIn('initial', result)
        self.assertIn('data', result)

    def test_get_context_data(self):
        kwargs = {'foo': 1, 'bar': 2}

        result = self.mixin.get_context_data(**kwargs)

        self.assertDictEqual(kwargs, result)

    def test_get_success_url(self):
        url = 'http://www.foo.bar'
        self.mixin.success_url = url

        result = self.mixin.get_success_url()

        self.assertEqual(url, result)

    def test_get_success_url_fail(self):
        self.mixin.success_url = None

        self.assertRaises(ImproperlyConfigured, self.mixin.get_success_url)

    @patch.object(AjaxFormMixin, 'error_response')
    def test_form_invalid(self, error_response_mock):
        form = MagicMock()
        errors = OrderedDict()
        errors['foo'] = 'foobar'
        errors['bar'] = 'barfoo'
        form.errors = errors

        self.mixin.form_invalid(form)

        expected_call = call('Error in fields: foo, bar')
        self.assertEqual(error_response_mock.call_count, 1)
        self.assertEqual(error_response_mock.call_args, expected_call)

    @patch('audit_tools.audit.views.api.mixins.json')
    @patch.object(AjaxFormMixin, 'response_class')
    def test_error_response(self, response_class_mock, json_mock):
        msg = 'foo'
        kwargs = {'foo': 'bar'}
        expected_context = '{"status": 400, "general_message": "foo", "success": false}'
        json_mock.dumps.return_value = expected_context
        expected_kwargs = {'foo': 'bar', 'content_type': 'application/json', 'status': 400}

        self.mixin.error_response(msg, **kwargs)

        context_result = response_class_mock.call_args[0][0]
        kwargs_result = response_class_mock.call_args[1]
        self.assertEqual(expected_context, context_result)
        self.assertDictEqual(expected_kwargs, kwargs_result)

    def test_order_query(self):
        self.mixin.order_by = 'id'
        queryset = MagicMock()
        queryset.order_by.return_value = queryset
        self.mixin.queryset = queryset

        self.mixin.order_query()

        self.assertEqual(self.mixin.queryset, queryset)
        self.assertEqual(queryset.order_by.call_count, 1)

    def tearDown(self):
        pass
