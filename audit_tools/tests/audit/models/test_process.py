from __future__ import unicode_literals

import datetime
from unittest import TestCase

from audit_tools.audit.models import Process


class Foo(object):
    pass


class ProcessTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.name = 'Foo process'
        cls.machine = 'Bar machine'
        cls.user = 'Foo user'
        cls.pid = 1
        cls.creation_time = datetime.datetime(2016, 1, 17, 19, 11, 0)

    def setUp(self):
        pass

    def test_items(self):
        items = [('name', self.name), ('machine', self.machine), ('user', self.user), ('pid', self.pid),
                 ('creation_time', self.creation_time)]
        process = Process(
            interlink_id=None,
            name=self.name,
            args=None,
            machine=self.machine,
            user=self.user,
            pid=self.pid,
            creation_time=self.creation_time,
        )

        result = process.items()

        self.assertEqual(items, result)

    def test_verbose_str(self):
        process = Process(
                interlink_id=None,
                name=self.name,
                args=None,
                machine=self.machine,
                user=self.user,
                pid=self.pid,
                creation_time=self.creation_time,
        )

        expected = 'Process {} with pid {:d} run by {} on {} ({})'.format(
                self.name, self.pid, self.user, self.machine, self.creation_time)
        self.assertEqual(expected, process.verbose_str())

    def test_str(self):
        process = Process(
                interlink_id=None,
                name=self.name,
                args=None,
                machine=self.machine,
                user=self.user,
                pid=self.pid,
                creation_time=self.creation_time,
        )

        expected = 'Process{{{}, pid:{:d}, user:{}, machine:{}, creation_time:{}}}'.format(
                self.name, self.pid, self.user, self.machine, self.creation_time)
        self.assertEqual(expected, str(process))

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass
