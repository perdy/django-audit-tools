from __future__ import unicode_literals

from django.test import TestCase
from mock import patch, call
from mongoengine import ConnectionError

from audit_tools.audit.db import mongodb_connect


@patch('audit_tools.audit.db.mongoengine')
class DBTestCase(TestCase):
    def setUp(self):
        pass

    def test_mongodb_connect_single_host(self, mongoengine_mock):
        connection = {
            'HOST': 'host',
            'PORT': 0,
            'NAME': 'foo'
        }
        alias = 'bar'

        mongodb_connect(connection, alias)

        calls = [call('foo', host='mongodb://host:0/foo', alias='bar')]
        self.assertEqual(mongoengine_mock.connect.call_args_list, calls)

    def test_mongodb_connect_multiple_host(self, mongoengine_mock):
        connection = {
            'HOST': ['host1', 'host2'],
            'PORT': [0, 1],
            'NAME': 'foo',
            'REPLICA_SET': 'replica'
        }
        alias = 'bar'

        mongodb_connect(connection, alias)

        calls = [call('foo', host='mongodb://host1:0,host2:1/foo?replicaSet=replica', alias='bar')]
        self.assertEqual(mongoengine_mock.connect.call_args_list, calls)

    def test_mongodb_connect_with_auth(self, mongoengine_mock):
        connection = {
            'USER': 'user',
            'PASSWORD': 'pass',
            'HOST': 'host',
            'PORT': 0,
            'NAME': 'foo'
        }
        alias = 'bar'

        mongodb_connect(connection, alias)

        calls = [call('foo', host='mongodb://user:pass@host:0/foo', alias='bar')]
        self.assertEqual(mongoengine_mock.connect.call_args_list, calls)

    @patch('audit_tools.audit.db.logger')
    def test_mongodb_connect_error(self, logger_mock, mongoengine_mock):
        mongoengine_mock.connect.side_effect = ConnectionError

        self.assertRaises(ConnectionError, mongodb_connect, {}, '')
        self.assertEqual(logger_mock.error.call_count, 1)

    def tearDown(self):
        pass
