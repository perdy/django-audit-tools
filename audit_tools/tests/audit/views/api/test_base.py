# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from unittest import TestCase

from mock import MagicMock, call, patch

from audit_tools.audit.views.api.base import ApiViewSet


@patch.object(ApiViewSet, 'get_form_class', return_value=None)
@patch.object(ApiViewSet, 'get_form', return_value=None)
@patch.object(ApiViewSet, 'queryset')
class ApiViewSetTestCase(TestCase):
    def setUp(self):
        self.view_set = ApiViewSet()

    def test_get_queryset_model_defined(self, queryset_mock, get_form_mock, get_form_class_mock):
        self.view_set.queryset = None
        self.view_set.model = MagicMock()

        self.view_set.get_queryset()

        self.assertEqual(self.view_set.model.objects.all.call_count, 1)

    def test_get_queryset(self, queryset_mock, get_form_mock, get_form_class_mock):
        self.view_set.model = MagicMock()

        self.view_set.get_queryset()

        self.assertEqual(self.view_set.model.objects.all.call_count, 0)

    @patch.object(ApiViewSet, 'filter_query')
    def test_get_queryset_form_valid(self, filter_query_mock, queryset_mock, get_form_mock, get_form_class_mock):
        filter_form = MagicMock()
        filter_form.is_valid.return_value = True
        get_form_mock.return_value = filter_form

        self.view_set.get_queryset()

        self.assertEqual(filter_query_mock.call_count, 1)

    @patch.object(ApiViewSet, 'form_invalid')
    def test_get_queryset_form_invalid(self, form_invalid_mock, queryset_mock, get_form_mock, get_form_class_mock):
        filter_form = MagicMock()
        filter_form.is_valid.return_value = False
        get_form_mock.return_value = filter_form

        self.view_set.get_queryset()

        self.assertEqual(form_invalid_mock.call_count, 1)

    @patch.object(ApiViewSet, 'order_query')
    def test_get_queryset_order_by(self, order_query_mock, queryset_mock, get_form_mock, get_form_class_mock):
        self.view_set.order_by = 'id'

        self.view_set.get_queryset()

        self.assertEqual(order_query_mock.call_count, 1)

    def tearDown(self):
        pass
