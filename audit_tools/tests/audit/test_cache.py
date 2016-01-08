from __future__ import unicode_literals

from django.test import TestCase
from mock import patch, MagicMock
from mongoengine import DoesNotExist

from audit_tools.audit.cache import cache
from audit_tools.audit.models import Process, Access


class CacheTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cache = cache
        cls.process = Process()
        cls.access = Access()

    def setUp(self):
        self.cache.namespace = MagicMock()

    def test_get_process_cached(self):
        self.cache.namespace.audit_current_process = self.process

        process = self.cache.get_process(None)

        self.assertEqual(self.process, process)

    @patch('audit_tools.audit.models.Process')
    def test_get_process_not_cached_exists(self, process_mock):
        self.cache.namespace.audit_current_process = None
        process_mock.objects.get.return_value = self.process

        data = {'pid': 'pid', 'machine': 'machine', 'creation_time': 'creation_time'}
        process = self.cache.get_process(data)

        self.assertEqual(self.process, process)

    @patch('audit_tools.audit.models.Process')
    def test_get_process_not_cached_not_exists(self, process_mock):
        p = MagicMock()
        self.cache.namespace.audit_current_process = None
        process_mock.objects.get.side_effect = DoesNotExist
        process_mock.return_value = p

        data = {'pid': 'pid', 'machine': 'machine', 'creation_time': 'creation_time'}
        process = self.cache.get_process(data)

        self.assertEqual(p, process)
        self.assertEqual(p.save.call_count, 1)

    def test_set_process(self):
        self.cache.set_process(self.process)

        self.assertTrue(hasattr(self.cache.namespace, 'audit_current_process'))
        self.assertTrue(isinstance(self.cache.namespace.audit_current_process, Process))
        self.assertEqual(self.cache.namespace.audit_current_process, self.process)

    def test_get_last_access_cached(self):
        self.cache.namespace.audit_current_access = self.access

        access = self.cache.get_last_access()

        self.assertEqual(self.access, access)

    def test_get_last_access_not_cached(self):
        self.cache.namespace.audit_current_access = None

        access = self.cache.get_last_access()

        self.assertIsNone(access)

    def test_set_last_access(self):
        self.cache.set_last_access(self.access)

        self.assertTrue(hasattr(self.cache.namespace, 'audit_current_access'))
        self.assertTrue(isinstance(self.cache.namespace.audit_current_access, Access))
        self.assertEqual(self.cache.namespace.audit_current_access, self.access)

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass
