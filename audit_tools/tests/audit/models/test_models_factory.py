from __future__ import unicode_literals

from unittest import TestCase

import datetime
from mock import patch, MagicMock, call

from audit_tools.audit.models import ACTIONS
from audit_tools.audit.models.models_factory import create_model_action, create_access, update_access, \
    _model_action_factory, _access_factory


class Foo(object):
    pass


class ModelsFactoryTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def test_create_model_action(self):
        model_action_data = {}
        access = MagicMock()
        process = MagicMock()
        model_action = MagicMock()

        with patch('audit_tools.audit.models.models_factory._model_action_factory', return_value=model_action)\
                as maf_mock:
            result = create_model_action(model_action_data, access, process)

        self.assertIn('access', model_action_data)
        self.assertIn('process', model_action_data)
        self.assertEqual(maf_mock.call_count, 1)
        self.assertEqual(result, model_action)

    def test_create_access(self):
        access_data = {}
        access = MagicMock()
        process_data = {}
        process = MagicMock()

        with patch('audit_tools.audit.models.models_factory._access_factory', return_value=access) as af_mock, \
                patch('audit_tools.audit.models.models_factory.cache') as cache_mock:
            cache_mock.get_process.return_value = process
            result = create_access(access_data, process_data)

        self.assertIn('process', access_data)
        self.assertEqual(cache_mock.get_process.call_count, 1)
        self.assertEqual(af_mock.call_count, 1)
        self.assertEqual(result, access)

    def test_update_access_request(self):
        access = MagicMock()
        attr = MagicMock()
        update_data = {'request': {}}

        with patch('audit_tools.audit.models.access.AccessRequest', return_value=attr) as attr_mock:
            result = update_access(access, **update_data)

        self.assertEqual(attr_mock.call_count, 1)
        self.assertEqual(result, access)
        self.assertEqual(access.request, attr)

    def test_update_access_time(self):
        access = MagicMock()
        attr = MagicMock()
        update_data = {'time': {}}

        with patch('audit_tools.audit.models.access.AccessTime', return_value=attr) as attr_mock:
            result = update_access(access, **update_data)

        self.assertEqual(attr_mock.call_count, 1)
        self.assertEqual(result, access)
        self.assertEqual(access.time, attr)

    def test_update_access_view(self):
        access = MagicMock()
        attr = MagicMock()
        update_data = {'view': {}}

        with patch('audit_tools.audit.models.access.AccessView', return_value=attr) as attr_mock:
            result = update_access(access, **update_data)

        self.assertEqual(attr_mock.call_count, 1)
        self.assertEqual(result, access)
        self.assertEqual(access.view, attr)

    def test_update_access_response(self):
        access = MagicMock()
        attr = MagicMock()
        update_data = {'response': {}}

        with patch('audit_tools.audit.models.access.AccessResponse', return_value=attr) as attr_mock:
            result = update_access(access, **update_data)

        self.assertEqual(attr_mock.call_count, 1)
        self.assertEqual(result, access)
        self.assertEqual(access.response, attr)

    def test_update_access_exception(self):
        access = MagicMock()
        attr = MagicMock()
        update_data = {'exception': {}}

        with patch('audit_tools.audit.models.access.AccessException', return_value=attr) as attr_mock:
            result = update_access(access, **update_data)

        self.assertEqual(attr_mock.call_count, 1)
        self.assertEqual(result, access)
        self.assertEqual(access.exception, attr)

    def test_update_access_process(self):
        access = MagicMock()
        attr = MagicMock()
        update_data = {'process': attr}

        result = update_access(access, **update_data)

        self.assertEqual(result, access)
        self.assertEqual(access.process, attr)

    def test_update_access_user(self):
        access = MagicMock()
        attr = MagicMock()
        update_data = {'user': {}}

        with patch('audit_tools.audit.models.access.AccessUser', return_value=attr) as attr_mock:
            result = update_access(access, **update_data)

        self.assertEqual(attr_mock.call_count, 1)
        self.assertEqual(result, access)
        self.assertEqual(access.user, attr)

    def test_update_access_custom(self):
        access = MagicMock()
        attr = MagicMock()
        update_data = {'custom': attr}

        result = update_access(access, **update_data)

        self.assertEqual(result, access)
        self.assertEqual(access.custom, attr)

    def test_model_action_factory(self):
        model = MagicMock()
        content = MagicMock()
        instance = MagicMock()
        model_action = MagicMock()
        timestamp = datetime.datetime(2016, 1, 17, 21, 13)

        with patch('audit_tools.audit.models.model_action.ModelActionModel', return_value=model) as model_mock,\
                patch('audit_tools.audit.models.model_action.ModelActionContent', return_value=content) \
                as content_mock,\
                patch('audit_tools.audit.models.model_action.ModelActionInstance', return_value=instance) \
                as instance_mock,\
                patch('audit_tools.audit.models.model_action.ModelAction', return_value=model_action) as ma_mock:
            result = _model_action_factory({}, ACTIONS.CREATE, {}, {}, timestamp, None, None)

        self.assertEqual(result, model_action)
        self.assertEqual(model_mock.call_count, 1)
        self.assertEqual(content_mock.call_count, 1)
        self.assertEqual(instance_mock.call_count, 1)
        self.assertEqual(ma_mock.call_count, 1)
        expected_call = call(access=None, action=ACTIONS.CREATE, content=content, instance=instance, model=model,
                             process=None, timestamp=timestamp)
        self.assertEqual(ma_mock.call_args, expected_call)

    def test_access_factory(self):
        access = MagicMock()
        exception = MagicMock()
        response = MagicMock()
        time = MagicMock()
        view = MagicMock()
        user = MagicMock()
        request = MagicMock()
        interlink_id = 'foo id'

        with patch('audit_tools.audit.models.access.AccessException', return_value=exception) as exc_mock,\
                patch('audit_tools.audit.models.access.AccessResponse', return_value=response) as res_mock, \
                patch('audit_tools.audit.models.access.AccessTime', return_value=time) as time_mock, \
                patch('audit_tools.audit.models.access.AccessView', return_value=view) as view_mock,\
                patch('audit_tools.audit.models.access.AccessUser', return_value=user) as user_mock, \
                patch('audit_tools.audit.models.access.Access', return_value=access) as access_mock:
            result = _access_factory(request, {'foo': 'bar'}, {'foo': 'bar'}, {'foo': 'bar'}, {'foo': 'bar'}, None,
                                     {'foo': 'bar'}, None, interlink_id)
        self.assertEqual(result, access)
        self.assertEqual(exc_mock.call_count, 1)
        self.assertEqual(res_mock.call_count, 1)
        self.assertEqual(time_mock.call_count, 1)
        self.assertEqual(view_mock.call_count, 1)
        self.assertEqual(user_mock.call_count, 1)
        self.assertEqual(access_mock.call_count, 1)
        expected_call = call(request=request, time=time, view=view, response=response, exception=exception,
                             process=None, user=user, custom=None, interlink_id=interlink_id)
        self.assertEqual(access_mock.call_args, expected_call)

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass
