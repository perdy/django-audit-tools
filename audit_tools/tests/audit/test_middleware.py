from __future__ import unicode_literals
from bson.json_util import dumps
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse

from django.test import TestCase
from mock import patch

from audit_tools.audit.middleware import AuditMiddleware


class MiddlewareTestCase(TestCase):
    def setUp(self):
        self.middleware = AuditMiddleware()

    @patch('audit_tools.audit.middleware.settings')
    def test_black_list(self, settings):
        settings.BLACKLIST = {'': ('blacklist', )}
        bl = self.middleware._check_blacklist('/test')
        self.assertFalse(bl)

        bl = self.middleware._check_blacklist('/blacklist/')
        self.assertTrue(bl)

        bl = self.middleware._check_blacklist('/test/blacklist')
        self.assertTrue(bl)

        bl = self.middleware._check_blacklist('/blacklisttest')
        self.assertTrue(bl)

        bl = self.middleware._check_blacklist('/black/list')
        self.assertFalse(bl)

    def test_function_based_view(self):
        # Fake function-based view
        def view_func(*args, **kwargs):
            return None
        view_args = []
        view_kwargs = {}

        # Do process view
        view_data = self.middleware._extract_view_data(view_func, view_args, view_kwargs)

        # Check if view data is extracted successfully
        self.assertEqual(view_data['full_name'], __name__ + '.view_func')
        self.assertEqual(view_data['app'], __name__.split('.', 1)[0])
        self.assertEqual(view_data['name'], 'view_func')
        self.assertEqual(view_data['args'], [])
        self.assertEqual(view_data['kwargs'], {})

    def test_class_based_view(self):
        # Fake class-based view
        class View(object):
            def view_func(self, *args, **kwargs):
                return None

        view_class = View()
        view_args = []
        view_kwargs = {}

        # Do process view
        view_data = self.middleware._extract_view_data(view_class.view_func, view_args, view_kwargs)

        # Check if view data is extracted successfully
        self.assertEqual(view_data['full_name'], __name__ + '.View')
        self.assertEqual(view_data['app'], __name__.split('.', 1)[0])
        self.assertEqual(view_data['name'], 'View')
        self.assertEqual(view_data['args'], [])
        self.assertEqual(view_data['kwargs'], {})

    def test_user_valid(self):
        request = HttpRequest()
        request.user = User(username='test_user', id=123)

        user_data = self.middleware._extract_user_data(request)

        self.assertEqual(user_data['id'], 123)
        self.assertEqual(user_data['username'], 'test_user')

    def test_user_invalid(self):
        request = HttpRequest()
        request.user = User.objects.none()

        user_data = self.middleware._extract_user_data(request)

        self.assertEqual(user_data['id'], -1)
        self.assertEqual(user_data['username'], 'Anonymous')

    @patch('audit_tools.audit.middleware.save_access')
    def test_process_request_disabled(self, save_access):
        request = HttpRequest()
        view_func = lambda: None
        view_func.disable_audit = True
        view_args = []
        view_kwargs = {}
        self.middleware.process_view(request, view_func, view_args, view_kwargs)

        # Check that no save has done.
        self.assertEqual(save_access.call_count, 0)
        self.assertEqual(save_access.apply_async.call_count, 0)
        self.assertTrue(self.middleware._disabled)

    @patch('audit_tools.audit.middleware.save_access')
    @patch('audit_tools.audit.middleware.settings')
    def test_process_request_blacklisted(self, settings, save_access):
        # Add blacklist setting
        settings.BLACKLIST = {'': ('blacklist', )}

        request = HttpRequest()
        request.path = '/blacklist/'
        view_func = lambda: None
        view_args = []
        view_kwargs = {}
        self.middleware.process_view(request, view_func, view_args, view_kwargs)

        # Check that no save has done.
        self.assertEqual(save_access.call_count, 0)
        self.assertEqual(save_access.apply_async.call_count, 0)
        self.assertTrue(self.middleware._blacklisted)

    @patch('audit_tools.audit.middleware.create_access')
    @patch('audit_tools.audit.middleware.save_access')
    @patch('audit_tools.audit.middleware.settings')
    def test_process_request_sync(self, settings, save_access, create_access):
        # Add sync setting
        settings.RUN_ASYNC = False

        request = HttpRequest()
        view_func = lambda: None
        view_args = []
        view_kwargs = {}
        self.middleware.process_view(request, view_func, view_args, view_kwargs)

        # Check that create access method that make the object in Audit database is called
        self.assertEqual(create_access.call_count, 1)

        # Check that sync call is done and async call isn't
        self.assertEqual(save_access.call_count, 1)
        self.assertEqual(save_access.apply_async.call_count, 0)

    @patch('audit_tools.audit.middleware.create_access')
    @patch('audit_tools.audit.middleware.save_access')
    @patch('audit_tools.audit.middleware.settings')
    def test_process_request_async(self, settings, save_access, create_access):
        # Add sync setting
        settings.RUN_ASYNC = True

        request = HttpRequest()
        view_func = lambda: None
        view_args = []
        view_kwargs = {}

        self.middleware.process_view(request, view_func, view_args, view_kwargs)

        # Check that create access method that make the object in Audit database is called
        self.assertEqual(create_access.call_count, 1)

        # Check that async call is done and sync call isn't
        self.assertEqual(save_access.call_count, 0)
        self.assertEqual(save_access.apply_async.call_count, 1)

    def test_response_html(self):
        # Create a html response object
        html_template = "<!DOCTYPE html><html><head><title>Title</title></head><body>Page</body></html>"
        response = HttpResponse(html_template)

        response_data = self.middleware._extract_response_data(response)

        self.assertIn('html', response_data['type'])
        self.assertEqual(200, response_data['status_code'])
        self.assertIsNone(response_data['content'])

    def test_response_json(self):
        # Create a json response object
        json_dict = {'response': 'test'}
        json_template = dumps(json_dict)
        response = HttpResponse(json_template, content_type='application/json')

        response_data = self.middleware._extract_response_data(response)

        self.assertIn('json', response_data['type'])
        self.assertEqual(200, response_data['status_code'])
        self.assertEqual(json_dict, response_data['content'])

    def test_response_xml(self):
        # Create a xml response object
        xml_template = '<tag>test</tag>'
        response = HttpResponse(xml_template, content_type='application/xml')

        response_data = self.middleware._extract_response_data(response)

        self.assertIn('xml', response_data['type'])
        self.assertEqual(200, response_data['status_code'])
        self.assertEqual(xml_template, response_data['content'])

    @patch('audit_tools.audit.middleware.save_access')
    def test_process_response_disabled(self, save_access):
        # Process request
        request = HttpRequest()
        view_func = lambda: None
        view_func.disable_audit = True
        view_args = []
        view_kwargs = {}
        self.middleware.process_view(request, view_func, view_args, view_kwargs)

        # Process response
        response = HttpResponse()
        self.middleware.process_response(request, response)

        # Check that no save has done.
        self.assertEqual(save_access.call_count, 0)
        self.assertEqual(save_access.apply_async.call_count, 0)
        self.assertTrue(self.middleware._disabled)

    @patch('audit_tools.audit.middleware.save_access')
    @patch('audit_tools.audit.middleware.settings')
    def test_process_response_blacklisted(self, settings, save_access):
        # Add blacklist setting
        settings.BLACKLIST = {'': ('blacklist', )}

        # Process request
        request = HttpRequest()
        request.path = '/blacklist/'
        view_func = lambda: None
        view_args = []
        view_kwargs = {}
        self.middleware.process_view(request, view_func, view_args, view_kwargs)

        # Process response
        response = HttpResponse()
        self.middleware.process_response(request, response)

        # Check that no save has done.
        self.assertEqual(save_access.call_count, 0)
        self.assertEqual(save_access.apply_async.call_count, 0)
        self.assertTrue(self.middleware._blacklisted)

    @patch('audit_tools.audit.middleware.update_access')
    @patch('audit_tools.audit.middleware.save_access')
    @patch('audit_tools.audit.middleware.settings')
    def test_process_response_sync(self, settings, save_access, update_access):
        # Add sync setting
        settings.RUN_ASYNC = False

        request = HttpRequest()
        response = HttpResponse()
        self.middleware.process_response(request, response)

        # Check that sync call is done and async call isn't
        self.assertEqual(save_access.call_count, 1)
        self.assertEqual(save_access.apply_async.call_count, 0)

    @patch('audit_tools.audit.middleware.update_access')
    @patch('audit_tools.audit.middleware.save_access')
    @patch('audit_tools.audit.middleware.settings')
    def test_process_response_async(self, settings, save_access, update_access):
        # Add sync setting
        settings.RUN_ASYNC = True

        request = HttpRequest()
        response = HttpResponse()
        self.middleware.process_response(request, response)

        # Check that async call is done and sync call isn't
        self.assertEqual(save_access.call_count, 0)
        self.assertEqual(save_access.apply_async.call_count, 1)

    def test_python_exception(self):
        exception_message = 'Test exception'
        exception = Exception(exception_message)

        exception_data = self.middleware._extract_exception_data(exception)

        self.assertEqual(exception_data['type'], 'Exception')
        self.assertEqual(exception_data['message'], exception_message)
        self.assertEqual(exception_data['trace'], 'None\n')

    @patch('audit_tools.audit.middleware.save_access')
    def test_process_exception_disabled(self, save_access):
        # Process request
        request = HttpRequest()
        view_func = lambda: None
        view_func.disable_audit = True
        view_args = []
        view_kwargs = {}
        self.middleware.process_view(request, view_func, view_args, view_kwargs)

        # Process exception
        exception = Exception('Test exception')
        self.middleware.process_exception(request, exception)

        # Check that no save has done.
        self.assertEqual(save_access.call_count, 0)
        self.assertEqual(save_access.apply_async.call_count, 0)
        self.assertTrue(self.middleware._disabled)

    @patch('audit_tools.audit.middleware.save_access')
    @patch('audit_tools.audit.middleware.settings')
    def test_process_exception_blacklisted(self, settings, save_access):
        # Add blacklist setting
        settings.BLACKLIST = {'': ('blacklist', )}

        # Process request
        request = HttpRequest()
        request.path = '/blacklist/'
        view_func = lambda: None
        view_args = []
        view_kwargs = {}
        self.middleware.process_view(request, view_func, view_args, view_kwargs)

        # Process exception
        exception = Exception('Test exception')
        self.middleware.process_exception(request, exception)

        # Check that no save has done.
        self.assertEqual(save_access.call_count, 0)
        self.assertEqual(save_access.apply_async.call_count, 0)
        self.assertTrue(self.middleware._blacklisted)

    @patch('audit_tools.audit.middleware.update_access')
    @patch('audit_tools.audit.middleware.save_access')
    @patch('audit_tools.audit.middleware.settings')
    def test_process_exception_sync(self, settings, save_access, update_access):
        # Add sync setting
        settings.RUN_ASYNC = False

        request = HttpRequest()
        exception = Exception('Test exception')
        self.middleware.process_exception(request, exception)

        # Check that sync call is done and async call isn't
        self.assertEqual(save_access.call_count, 1)
        self.assertEqual(save_access.apply_async.call_count, 0)

    @patch('audit_tools.audit.middleware.update_access')
    @patch('audit_tools.audit.middleware.save_access')
    @patch('audit_tools.audit.middleware.settings')
    def test_process_exception_async(self, settings, save_access, update_access):
        # Add sync setting
        settings.RUN_ASYNC = True

        request = HttpRequest()
        exception = Exception('Test exception')
        self.middleware.process_exception(request, exception)

        # Check that async call is done and sync call isn't
        self.assertEqual(save_access.call_count, 0)
        self.assertEqual(save_access.apply_async.call_count, 1)

    def tearDown(self):
        pass