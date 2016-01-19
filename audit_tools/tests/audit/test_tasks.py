from __future__ import unicode_literals

from django.test import TestCase
from mock import patch, MagicMock
from mongoengine import ValidationError

from audit_tools.audit import tasks


@patch('audit_tools.audit.tasks.logger')
class AccessTaskTestCase(TestCase):
    def setUp(self):
        pass

    def test_save_ok(self, logger):
        access = MagicMock()
        access.save.return_value = True

        result = tasks.save_access(access)

        self.assertEqual(access.save.call_count, 1)
        self.assertTrue(result)

    def test_save_fail(self, logger):
        access = MagicMock()
        access.save.side_effect = Exception

        tasks.save_access(access)

        self.assertEqual(logger.exception.call_count, 1)

    def tearDown(self):
        pass


@patch('audit_tools.audit.models.models_factory.create_model_action')
@patch('audit_tools.audit.models.Access')
@patch('audit_tools.audit.tasks.logger')
class ModelActionTaskTestCase(TestCase):
    def setUp(self):
        pass

    def test_save_with_access(self, logger, access_klass, create_model_action):
        model_action = MagicMock()
        model_action.save.return_value = True
        create_model_action.return_value = model_action
        access = MagicMock()
        access.id = 1
        access.save.return_value = True
        access_klass.objects.get.return_value = access

        result = tasks.save_model_action(model_action, access, None)

        self.assertEqual(model_action.save.call_count, 1)
        self.assertTrue(result)

    def test_save_with_access_not_saved(self, logger, access_klass, create_model_action):
        model_action = MagicMock()
        model_action.save.return_value = True
        create_model_action.return_value = model_action
        access = MagicMock()
        access.save.return_value = True
        access_klass.objects.get.side_effect = (ValidationError, access)

        result = tasks.save_model_action(model_action, access, None)

        self.assertEqual(access.save.call_count, 1)
        self.assertTrue(result)

    def test_save_without_access(self, logger, access_klass, create_model_action):
        model_action = MagicMock()
        model_action.save.return_value = True
        create_model_action.return_value = model_action

        result = tasks.save_model_action(model_action, None, None)

        self.assertEqual(model_action.save.call_count, 1)
        self.assertTrue(result)

    def test_save_fail(self, logger, access_klass, create_model_action):
        model_action = MagicMock()
        access = MagicMock()
        access.id = 1
        access_klass.objects.get.side_effect = Exception

        result = tasks.save_model_action(model_action, access, None)

        self.assertEqual(logger.exception.call_count, 1)
        self.assertTrue(result)

    def tearDown(self):
        pass
