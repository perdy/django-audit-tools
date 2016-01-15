from __future__ import unicode_literals

from unittest import TestCase

import datetime
from django.contrib.auth.models import User
from mock import patch, MagicMock

from audit_tools.audit.models import Access
from audit_tools.audit.models.access import AccessRequest, AccessView, AccessUser, AccessResponse, AccessException, \
    AccessTime


def foo():
    pass


class AccessTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url = 'http://www.foo.bar'

        # View
        cls.view_full_name = "{}.{}".format(foo.__module__, foo.__name__)
        cls.view_name = foo.__name__
        cls.view_app = foo.__module__.split('.', 1)[0]

        # User
        cls.user_id = 1
        cls.user_username = 'foo user'

        # Response
        cls.response_content = 'foo response'
        cls.response_type = 'text'
        cls.response_status_code = 200

        # Exception
        cls.exception_type = 'foo exception'
        cls.exception_message = 'bar exception'
        cls.exception_trace = 'foobar exception'

        # Request
        cls.time_request = datetime.datetime(2016, 1, 15, 23, 24, 0)

        cls.access_request = AccessRequest(path=cls.url)
        cls.access_view = AccessView(full_name=cls.view_full_name, name=cls.view_name, app=cls.view_app)
        cls.access_user = AccessUser(id=cls.user_id, username=cls.user_username)
        cls.access_response = AccessResponse(content=cls.response_content, type=cls.response_type,
                                             status_code=cls.response_status_code)
        cls.access_exception = AccessException(type=cls.exception_type, message=cls.exception_message,
                                               trace=cls.exception_trace)
        cls.access_time = AccessTime(request=cls.time_request)

    def setUp(self):
        pass

    def test_url(self):
        access = Access(
                interlink_id=None,
                request=self.access_request,
                response=None,
                exception=None,
                time=None,
                view=None,
                user=None,
                custom=None,
                process=None,
        )

        # Test getter
        self.assertEqual(self.url, access.url)

        # Test setter
        url2 = 'http://www.bar.foo'
        access.url = url2
        self.assertEqual(url2, access.url)

        # Test deleter
        del access.url
        self.assertIsNone(access.url)

        # Let AccessRequest in his old status
        access.url = self.url

    def test_get_view(self):
        access = Access(
                interlink_id=None,
                request=None,
                response=None,
                exception=None,
                time=None,
                view=self.access_view,
                user=None,
                custom=None,
                process=None,
        )

        # Test getter
        self.assertEqual(foo, access.get_view())

    @patch('audit_tools.audit.models.access.User')
    def test_get_user(self, user_mock):
        user = MagicMock()
        user_mock.objects.get.return_value = user

        access = Access(
                interlink_id=None,
                request=None,
                response=None,
                exception=None,
                time=None,
                view=None,
                user=self.access_user,
                custom=None,
                process=None,
        )

        self.assertEqual(user, access.get_user())

    @patch('audit_tools.audit.models.access.User')
    def test_get_user_anonymous(self, user_mock):
        user_mock.objects.get.side_effect = User.DoesNotExist

        access = Access(
                interlink_id=None,
                request=None,
                response=None,
                exception=None,
                time=None,
                view=None,
                user=self.access_user,
                custom=None,
                process=None,
        )

        self.assertIsNone(access.get_user())

    def test_is_response(self):
        access = Access(
                interlink_id=None,
                request=None,
                response=self.access_response,
                exception=None,
                time=None,
                view=None,
                user=None,
                custom=None,
                process=None,
        )

        self.assertTrue(access.is_response())

    def test_is_not_response(self):
        access = Access(
                interlink_id=None,
                request=None,
                response=None,
                exception=None,
                time=None,
                view=None,
                user=None,
                custom=None,
                process=None,
        )

        self.assertFalse(access.is_response())

    def test_is_exception(self):
        access = Access(
                interlink_id=None,
                request=None,
                response=None,
                exception=self.access_exception,
                time=None,
                view=None,
                user=None,
                custom=None,
                process=None,
        )

        self.assertTrue(access.is_exception())

    def test_is_not_exception(self):
        access = Access(
                interlink_id=None,
                request=None,
                response=None,
                exception=None,
                time=None,
                view=None,
                user=None,
                custom=None,
                process=None,
        )

        self.assertFalse(access.is_exception())

    def test_items(self):
        items = [('foo', 'bar')]
        access = Access(
                interlink_id=None,
                request=None,
                response=None,
                exception=None,
                time=None,
                view=None,
                user=None,
                custom=None,
                process=None,
        )

        print(access.items())

        items_mock = MagicMock()
        items_mock.items.return_value = items
        with patch.object(Access, 'to_mongo', return_value=items_mock) as mongo_mock:
            result = access.items()

            self.assertEqual(items, result)
            self.assertEqual(mongo_mock.call_count, 1)
            self.assertEqual(items_mock.items.call_count, 1)

    def test_verbose_str(self):
        access = Access(
                interlink_id=None,
                request=self.access_request,
                response=None,
                exception=None,
                time=self.access_time,
                view=self.access_view,
                user=self.access_user,
                custom=None,
                process=None,
        )

        expected = 'Access to view {} from app {} mapped to url {} by user {} ({})'.format(
                self.view_name, self.view_app, self.url, self.user_username, self.time_request)
        print(self.access_request.path)
        self.assertEqual(expected, access.verbose_str())

    def test_str(self):
        access = Access(
                interlink_id=None,
                request=self.access_request,
                response=None,
                exception=None,
                time=self.access_time,
                view=self.access_view,
                user=self.access_user,
                custom=None,
                process=None,
        )

        expected = 'Access{{{}, user:{}, url:{}, time:{}}}'.format(
                self.view_full_name, self.user_username, self.url, self.time_request)
        self.assertEqual(expected, str(access))

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass


class AccessTimeTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def test_items(self):
        items = [('foo', 'bar')]

        access_time = AccessTime(request=datetime.datetime(2016, 1, 15, 23, 24, 0))

        items_mock = MagicMock()
        items_mock.items.return_value = items
        with patch.object(AccessTime, 'to_mongo', return_value=items_mock) as mongo_mock:
            result = access_time.items()

            self.assertEqual(items, result)
            self.assertEqual(mongo_mock.call_count, 1)
            self.assertEqual(items_mock.items.call_count, 1)

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass


class AccessViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def test_items(self):
        full_name = "{}.{}".format(foo.__module__, foo.__name__)
        name = foo.__name__
        app = foo.__module__.split('.', 1)[0]
        items = [('full_name', full_name), ('app', app), ('name', name), ('args', []), ('kwargs', {})]

        access_view = AccessView(full_name=full_name, app=app, name=name)

        self.assertEqual(items, access_view.items())

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass


class AccessUserTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def test_items(self):
        id_ = 1
        username = 'foo'
        items = [('id', id_), ('username', username)]

        access_user = AccessUser(id=id_, username=username)

        self.assertEqual(items, access_user.items())

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass


class AccessResponseTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def test_items(self):
        content = 'foo'
        type_ = 'text'
        status_code = 200

        items = [('content', content), ('type', type_), ('status_code', status_code)]

        access_response = AccessResponse(content=content, type=type_, status_code=status_code)

        self.assertEqual(items, access_response.items())

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass


class AccessExceptionTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def test_items(self):
        type_ = 'foo'
        message = 'bar'
        trace = 'foobar'

        items = [('type', type_), ('message', message), ('trace', trace)]

        access_exception = AccessException(type=type_, message=message, trace=trace)

        self.assertEqual(items, access_exception.items())

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass


class AccessRequestTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def test_items(self):
        path = 'http://www.foo.bar'
        items = [('path', path), ('GET', {}), ('POST', {}), ('COOKIES', {}), ('METADATA', {})]

        access_request = AccessRequest(path=path)

        self.assertEqual(items, access_request.items())

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass
