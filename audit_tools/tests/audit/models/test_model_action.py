from __future__ import unicode_literals

import datetime
from unittest import TestCase

from mock import patch, MagicMock

from audit_tools.audit.models import ACTIONS
from audit_tools.audit.models.model_action import ModelActionContent, ModelActionModel, ModelActionInstance, ModelAction


class Foo(object):
    pass


class ModelActionTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        # Action
        cls.action = ACTIONS.UPDATE

        # Model
        cls.model_full_name = "{}.{}".format(Foo.__module__, Foo.__name__)
        cls.model_name = Foo.__name__
        cls.model_app = Foo.__module__.split('.', 1)[0]

        # Content
        cls.content_old = {'foo': 'foo'}
        cls.content_new = {'foo': 'bar'}
        cls.content_changes = {'foo': {'old': 'foo', 'new': 'bar'}}

        # Instance
        cls.instance_id = '1'
        cls.instance_description = 'foo instance'

        # Request
        cls.timestamp = datetime.datetime(2016, 1, 17, 18, 16, 0)

        cls.ma_model = ModelActionModel(full_name=cls.model_full_name, name=cls.model_name, app=cls.model_app)
        cls.ma_content = ModelActionContent(old=cls.content_old, new=cls.content_new, changes=cls.content_changes)
        cls.ma_instance = ModelActionInstance(id=cls.instance_id, description=cls.instance_description)

    def setUp(self):
        pass

    def test_changes(self):
        model_action = ModelAction(
                model=None,
                action=self.action,
                content=self.ma_content,
                instance=None,
                timestamp=None,
                access=None,
                process=None,
        )

        # Test getter
        self.assertEqual(self.content_changes, model_action.changes)

        # Test setter
        changes = {}
        model_action.changes = changes
        self.assertEqual(changes, model_action.changes)

        # Test deleter
        del model_action.changes
        self.assertEqual({}, model_action.changes)

        # Let AccessRequest in his old status
        model_action.changes = self.content_changes

    def test_get_model(self):
        model_action = ModelAction(
                model=self.ma_model,
                action=self.action,
                content=self.ma_content,
                instance=None,
                timestamp=None,
                access=None,
                process=None,
        )

        # Test getter
        self.assertEqual(Foo, model_action.get_model())

    @patch('audit_tools.audit.models.model_action.dynamic_import', side_effect=Exception)
    def test_get_model_fail(self, dynamic_import_mock):
        model_action = ModelAction(
                model=self.ma_model,
                action=self.action,
                content=self.ma_content,
                instance=None,
                timestamp=None,
                access=None,
                process=None,
        )

        # Test getter
        self.assertRaises(TypeError, model_action.get_model)

    def test_get_instance(self):
        model_action = ModelAction(
                model=self.ma_model,
                action=self.action,
                content=self.ma_content,
                instance=self.ma_instance,
                timestamp=None,
                access=None,
                process=None,
        )

        foo = Foo()
        with patch('audit_tools.tests.audit.models.test_model_action.Foo') as model_mock:
            model_mock.objects.get.return_value = foo
            self.assertEqual(foo, model_action.get_instance())

    def test_get_instance_fail(self):
        model_action = ModelAction(
                model=self.ma_model,
                action=self.action,
                content=self.ma_content,
                instance=None,
                timestamp=None,
                access=None,
                process=None,
        )

        with patch('audit_tools.tests.audit.models.test_model_action.Foo') as model_mock:
            model_mock.objects.get.side_effect = Exception
            self.assertIsNone(model_action.get_instance())

    def test_items(self):
        items = [('foo', 'bar')]
        model_action = ModelAction(
                model=None,
                action=self.action,
                content=self.ma_content,
                instance=None,
                timestamp=None,
                access=None,
                process=None,
        )

        items_mock = MagicMock()
        items_mock.items.return_value = items
        with patch.object(ModelAction, 'to_mongo', return_value=items_mock) as mongo_mock:
            result = model_action.items()

            self.assertEqual(items, result)
            self.assertEqual(mongo_mock.call_count, 1)
            self.assertEqual(items_mock.items.call_count, 1)

    def test_verbose_str(self):
        model_action = ModelAction(
                model=self.ma_model,
                action=self.action,
                content=self.ma_content,
                instance=self.ma_instance,
                timestamp=self.timestamp,
                access=None,
                process=None,
        )

        expected = '{} instance {} of model {} from app {} ({})'.format(
                self.action, self.instance_id, self.model_name, self.model_app, self.timestamp)
        self.assertEqual(expected, model_action.verbose_str())

    def test_str(self):
        model_action = ModelAction(
                model=self.ma_model,
                action=self.action,
                content=self.ma_content,
                instance=self.ma_instance,
                timestamp=self.timestamp,
                access=None,
                process=None,
        )

        expected = 'ModelAction{{{}({}), action:{}, time:{}}}'.format(
                self.model_full_name, self.instance_id, self.action, self.timestamp)
        self.assertEqual(expected, str(model_action))

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass


class ModelActionModelTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def test_items(self):
        model_full_name = "{}.{}".format(Foo.__module__, Foo.__class__.__name__)
        model_name = Foo.__class__.__name__
        model_app = Foo.__module__.split('.', 1)[0]

        items = [('full_name', model_full_name), ('app', model_app), ('name', model_name)]

        ma_model = ModelActionModel(full_name=model_full_name, app=model_app, name=model_name)

        result = ma_model.items()

        self.assertEqual(items, result)

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass


class ModelActionContentTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def test_items(self):
        content_old = {'foo': 'foo'}
        content_new = {'foo': 'bar'}
        content_changes = {'foo': {'old': 'foo', 'new': 'bar'}}
        items = [('old', content_old), ('new', content_new), ('changes', content_changes)]

        ma_content = ModelActionContent(old=content_old, new=content_new, changes=content_changes)

        self.assertEqual(items, ma_content.items())

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass


class ModelActionInstanceTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def test_items(self):
        id_ = '1'
        description = 'foo'
        items = [('id', id_), ('description', description)]

        ma_instance = ModelActionInstance(id=id_, description=description)

        self.assertEqual(items, ma_instance.items())

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass
