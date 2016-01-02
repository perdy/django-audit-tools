from __future__ import unicode_literals

from django.test import TestCase
from mock import patch

from audit.middleware import AuditMiddleware


@patch('audit.middleware.settings')
class MiddlewareTestCase(TestCase):
    def setUp(self):
        self.middleware = AuditMiddleware()

    def test_black_list(self, settings):
        settings.BLACKLIST = {'': ('blacklist', )}
        bl = self.middleware._check_blacklist('/test')
        self.assertFalse(bl)

        bl = self.middleware._check_blacklist('/blacklist')
        self.assertTrue(bl)

        bl = self.middleware._check_blacklist('/test/blacklist')
        self.assertTrue(bl)

        bl = self.middleware._check_blacklist('/blacklisttest')
        self.assertTrue(bl)

    def test_process_request(self, settings):
        pass

    def test_process_response(self, settings):
        pass

    def test_process_exception(self, settings):
        pass

    def tearDown(self):
        pass