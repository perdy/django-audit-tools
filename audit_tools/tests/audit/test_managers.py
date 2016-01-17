from __future__ import unicode_literals

from unittest import TestCase

from mock import patch, call

from audit_tools.audit.managers import _check_args, ModelActionQuerySet, AccessQuerySet


class TestModel(object):
    def __init__(self, pk=0):
        self.pk = pk


class TestModel2(object):
    pass


def test_view():
    pass


class TestException(Exception):
    pass


class CheckArgsTestCase(TestCase):
    def setUp(self):
        pass

    def test_check_required_arg(self):
        required = 'foo'
        kwargs = {'bar': 'bar'}

        self.assertRaises(AttributeError, _check_args, required, None, kwargs)

    def test_check_incompatible_args(self):
        incompatible = ('foo', 'bar')
        kwargs = {'foo': 'foo'}

        self.assertRaises(AttributeError, _check_args, 'foo', incompatible, kwargs)

    def test_check_args(self):
        required = 'foo'
        incompatible = ('bar',)
        kwargs = {'foo': 'foo'}

        res = _check_args(required, incompatible, kwargs)

        self.assertSequenceEqual(res, ('foo', 'foo'))

    def tearDown(self):
        pass


class ModelActionQuerySetTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('mongoengine.queryset.base.BaseQuerySet.__init__', autospec=True, return_value=None):
            cls.queryset = ModelActionQuerySet(None, None)

    def setUp(self):
        pass

    def test_filter_by_model(self):
        kwargs = {
            'klass': TestModel,
        }
        expected = {
            'model__name': 'TestModel',
            'model__app': 'audit_tools',
        }

        with patch('mongoengine.queryset.base.BaseQuerySet.filter') as filter_mock:
            self.queryset.filter_by_model(**kwargs)
            self.assertSequenceEqual(filter_mock.call_args_list, [call(**expected)])

    def test_get_by_model(self):
        kwargs = {
            'klass': TestModel,
        }
        expected = {
            'model__name': 'TestModel',
            'model__app': 'audit_tools',
        }

        with patch('mongoengine.queryset.base.BaseQuerySet.get') as get_mock:
            self.queryset.get_by_model(**kwargs)
            self.assertSequenceEqual(get_mock.call_args_list, [call(**expected)])

    def test_filter_by_model_list(self):
        kwargs = {
            'klass': (TestModel, TestModel2)
        }
        expected = {
            'model__full_name': 'audit_tools.tests.audit.test_managers.TestModel|'
                                'audit_tools.tests.audit.test_managers.TestModel2',
        }

        with patch('mongoengine.queryset.base.BaseQuerySet.filter') as filter_mock:
            self.queryset.filter_by_model_list(**kwargs)
            c = filter_mock.call_args
            args, kwargs = c
            kwargs_pattern = kwargs['model__full_name'].pattern
            self.assertEqual(kwargs_pattern, expected['model__full_name'])

    def test_get_by_model_list(self):
        kwargs = {
            'klass': (TestModel, TestModel2)
        }
        expected = {
            'model__full_name': 'audit_tools.tests.audit.test_managers.TestModel|'
                                'audit_tools.tests.audit.test_managers.TestModel2',
        }

        with patch('mongoengine.queryset.base.BaseQuerySet.get') as get_mock:
            self.queryset.get_by_model_list(**kwargs)
            c = get_mock.call_args
            args, kwargs = c
            kwargs_pattern = kwargs['model__full_name'].pattern
            self.assertEqual(kwargs_pattern, expected['model__full_name'])

    def test_filter_by_instance(self):
        instance = TestModel(pk=0)
        kwargs = {
            'obj': instance,
        }
        expected = {
            'instance__id': '0',
            'model__name': 'TestModel',
            'model__app': 'audit_tools',
        }

        with patch('mongoengine.queryset.base.BaseQuerySet.filter') as filter_mock:
            self.queryset.filter_by_instance(**kwargs)
            self.assertSequenceEqual(filter_mock.call_args_list, [call(**expected)])

    def test_get_by_instance(self):
        instance = TestModel(pk=0)
        kwargs = {
            'obj': instance,
        }
        expected = {
            'instance__id': '0',
            'model__name': 'TestModel',
            'model__app': 'audit_tools',
        }

        with patch('mongoengine.queryset.base.BaseQuerySet.get') as get_mock:
            self.queryset.get_by_instance(**kwargs)
            self.assertSequenceEqual(get_mock.call_args_list, [call(**expected)])

    def tearDown(self):
        pass


class AccessQuerySetTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        with patch('mongoengine.queryset.base.BaseQuerySet.__init__', autospec=True, return_value=None):
            cls.queryset = AccessQuerySet(None, None)

    def test_filter_by_view(self):
        kwargs = {
            'fview': test_view,
        }
        expected = {
            'view__full_name': 'audit_tools.tests.audit.test_managers.test_view',
        }

        with patch('mongoengine.queryset.base.BaseQuerySet.filter') as filter_mock:
            self.queryset.filter_by_view(**kwargs)
            self.assertSequenceEqual(filter_mock.call_args_list, [call(**expected)])

    def test_get_by_view(self):
        kwargs = {
            'fview': test_view,
        }
        expected = {
            'view__full_name': 'audit_tools.tests.audit.test_managers.test_view',
        }

        with patch('mongoengine.queryset.base.BaseQuerySet.get') as get_mock:
            self.queryset.get_by_view(**kwargs)
            self.assertSequenceEqual(get_mock.call_args_list, [call(**expected)])

    def test_filter_by_url(self):
        kwargs = {
            'url': 'foo',
        }
        expected = {
            'request__path': 'foo',
        }

        with patch('mongoengine.queryset.base.BaseQuerySet.filter') as filter_mock:
            self.queryset.filter_by_url(**kwargs)
            self.assertSequenceEqual(filter_mock.call_args_list, [call(**expected)])

    def test_filter_by_url_regex(self):
        kwargs = {
            'url__regex': 'foo',
        }
        expected = {
            'request__path': 'foo',
        }

        with patch('mongoengine.queryset.base.BaseQuerySet.filter') as filter_mock:
            self.queryset.filter_by_url(**kwargs)
            c = filter_mock.call_args
            args, kwargs = c
            kwargs_pattern = kwargs['request__path'].pattern
            self.assertEqual(kwargs_pattern, expected['request__path'])

    def test_filter_by_url_modifier(self):
        kwargs = {
            'url__modifier': 'foo',
        }
        expected = {
            'request__path__modifier': 'foo',
        }

        with patch('mongoengine.queryset.base.BaseQuerySet.filter') as filter_mock:
            self.queryset.filter_by_url(**kwargs)
            self.assertSequenceEqual(filter_mock.call_args_list, [call(**expected)])

    def test_get_by_url(self):
        kwargs = {
            'url': 'foo',
        }
        expected = {
            'request__path': 'foo',
        }

        with patch('mongoengine.queryset.base.BaseQuerySet.get') as get_mock:
            self.queryset.get_by_url(**kwargs)
            self.assertSequenceEqual(get_mock.call_args_list, [call(**expected)])

    def test_filter_by_exception(self):
        kwargs = {
            'exc': TestException,
        }
        expected = {
            'exception__type': 'TestException',
        }

        with patch('mongoengine.queryset.base.BaseQuerySet.filter') as filter_mock:
            self.queryset.filter_by_exception(**kwargs)
            self.assertSequenceEqual(filter_mock.call_args_list, [call(**expected)])

    def test_get_by_exception(self):
        kwargs = {
            'exc': TestException,
        }
        expected = {
            'exception__type': 'TestException',
        }

        with patch('mongoengine.queryset.base.BaseQuerySet.get') as get_mock:
            self.queryset.get_by_exception(**kwargs)
            self.assertSequenceEqual(get_mock.call_args_list, [call(**expected)])

    @classmethod
    def tearDownClass(cls):
        pass
