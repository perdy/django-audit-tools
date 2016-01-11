# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from mock import patch, MagicMock, PropertyMock

from audit_tools.audit.permissions import AUDIT_PERMISSIONS, register_permissions, unregister_permissions, SearchAccess, \
    ApiAccess


@patch('audit_tools.audit.permissions.ContentType')
@patch('audit_tools.audit.permissions.Permission')
@patch('audit_tools.audit.permissions.logger')
class PermissionRegistrationTestCase(TestCase):
    def setUp(self):
        pass

    def test_register(self, logger_mock, permission_mock, content_type_mock):
        content_type_mock.objects.get_or_create.return_value = (None, False)
        permission_mock.objects.get_or_create.return_value = (None, False)

        warn_expected = 1 + len(AUDIT_PERMISSIONS)

        res = register_permissions()

        self.assertEqual(logger_mock.warn.call_count, warn_expected)
        self.assertTrue(res)

    def test_register_registered_yet(self, logger_mock, permission_mock, content_type_mock):
        content_type_mock.objects.get_or_create.return_value = (None, True)
        permission_mock.objects.get_or_create.return_value = (None, True)

        warn_expected = 0

        res = register_permissions()

        self.assertEqual(logger_mock.warn.call_count, warn_expected)
        self.assertTrue(res)

    def test_register_fail(self, logger_mock, permission_mock, content_type_mock):
        content_type_mock.objects.get_or_create.side_effect = Exception

        error_expected = 1

        res = register_permissions()

        self.assertEqual(logger_mock.exception.call_count, error_expected)
        self.assertFalse(res)

    def test_unregister(self, logger_mock, permission_mock, content_type_mock):
        content_type_obj = MagicMock()
        content_type_mock.objects.get.return_value = content_type_obj
        permissions_queryset = MagicMock()
        permission_mock.objects.filter.return_value = permissions_queryset
        content_type_queryset = MagicMock()
        content_type_mock.objects.filter.return_value = content_type_queryset

        res = unregister_permissions()

        self.assertEqual(content_type_queryset.delete.call_count, 1)
        self.assertEqual(permissions_queryset.delete.call_count, 1)
        self.assertTrue(res)

    def test_unregister_not_registered(self, logger_mock, permission_mock, content_type_mock):
        content_type_mock.objects.get.side_effect = ContentType.DoesNotExist
        content_type_mock.DoesNotExist = ContentType.DoesNotExist

        res = unregister_permissions()

        self.assertEqual(logger_mock.exception.call_count, 1)
        self.assertFalse(res)

    def tearDown(self):
        pass


class SearchAccessPermissionTestCase(TestCase):
    def setUp(self):
        pass

    def test_has_permission(self):
        request = MagicMock()
        user = MagicMock()
        user.is_authenticated.return_value = True
        user.has_perm.return_value = True
        request.user = user

        res = SearchAccess().has_permission(request, None)

        self.assertTrue(res)

    def test_has_not_permission(self):
        request = MagicMock()
        user = MagicMock()
        user.is_authenticated.return_value = True
        user.has_perm.return_value = False
        request.user = user

        res = SearchAccess().has_permission(request, None)

        self.assertFalse(res)

    def test_is_not_authenticated(self):
        request = MagicMock()
        user = MagicMock()
        user.is_authenticated.return_value = False
        user.has_perm.return_value = True
        request.user = user

        res = SearchAccess().has_permission(request, None)

        self.assertFalse(res)

    def tearDown(self):
        pass


class ApiAccessPermissionTestCase(TestCase):
    def setUp(self):
        pass

    def test_has_permission(self):
        request = MagicMock()
        user = MagicMock()
        user.is_authenticated.return_value = True
        user.has_perm.return_value = True
        request.user = user

        res = ApiAccess().has_permission(request, None)

        self.assertTrue(res)

    def test_has_not_permission(self):
        request = MagicMock()
        user = MagicMock()
        user.is_authenticated.return_value = True
        user.has_perm.return_value = False
        request.user = user

        res = ApiAccess().has_permission(request, None)

        self.assertFalse(res)

    def test_is_not_authenticated(self):
        request = MagicMock()
        user = MagicMock()
        user.is_authenticated.return_value = False
        user.has_perm.return_value = True
        request.user = user

        res = ApiAccess().has_permission(request, None)

        self.assertFalse(res)

    def tearDown(self):
        pass
