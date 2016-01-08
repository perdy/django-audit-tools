from __future__ import unicode_literals

from unittest import TestCase

from mock import patch

from audit_tools.audit.decorators import DisableAudit, CheckActivate


@patch('audit_tools.audit.decorators.settings')
class CheckActivateTestCase(TestCase):
    def setUp(self):
        pass

    def test_activated(self, settings_mock):
        settings_mock.ACTIVATE = True

        @CheckActivate
        def foo():
            return 'foo'

        res = foo()

        self.assertEqual(res, 'foo')

    def test_deactivated(self, settings_mock):
        settings_mock.ACTIVATE = False

        @CheckActivate
        def foo():
            return 'foo'

        res = foo()

        self.assertEqual(res, None)

    def test_method_deactivated(self, settings_mock):
        settings_mock.ACTIVATE = False

        class Foo(object):
            @CheckActivate
            def bar(self):
                return 'bar'

        self.assertTrue(hasattr(Foo, 'bar'))
        self.assertEqual(Foo().bar(), None)

    def tearDown(self):
        pass


class DisableAuditTestCase(TestCase):
    def setUp(self):
        pass

    def test_enabled_view(self):
        def enabled():
            return 'Enabled'

        self.assertFalse(getattr(enabled, 'disable_audit', False))
        self.assertEqual(enabled(), 'Enabled')

    def test_disabled_view(self):
        @DisableAudit
        def disabled():
            return 'Disabled'

        self.assertTrue(getattr(disabled, 'disable_audit', False))
        self.assertEqual(disabled(), 'Disabled')

    def test_disabled_method_view(self):
        class TestView(object):
            @DisableAudit
            def disabled(self):
                return 'Disabled'

        view = TestView()

        self.assertTrue(getattr(TestView.disabled, 'disable_audit', False))
        self.assertEqual(view.disabled(), 'Disabled')

    def tearDown(self):
        pass
