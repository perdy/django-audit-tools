# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.db import models
from mock import patch, MagicMock

from audit_tools.audit import signals
from audit_tools.audit.utils import serialize_model_instance


class TestModel(models.Model):
    string_field = models.CharField(max_length=50)
    integer_field = models.IntegerField()
    float_field = models.FloatField()

    def __str__(self):
        return "ñ Unicode test ñ"


class SignalsTestCase(TestCase):
    def setUp(self):
        pass

    def test_model_data(self):
        model = TestModel()

        model_data = signals._extract_model_data(model)

        self.assertEqual(model_data['app'], 'audit_tools')
        self.assertEqual(model_data['name'], 'TestModel')
        self.assertEqual(model_data['full_name'], 'audit_tools.tests.audit.test_signals.TestModel')

    def test_content_create(self):
        model = TestModel()
        model.string_field = 'Test'
        model.integer_field = 1
        model.float_field = 1.0
        new_object = serialize_model_instance(model)
        keys = ['id', 'string_field', 'integer_field', 'float_field']

        content = signals._extract_content_data(None, new_object)

        self.assertItemsEqual(content['new'].keys(), keys)
        self.assertIsNone(content['old'])
        self.assertEqual(content['new']['string_field'], 'Test')
        self.assertEqual(content['new']['integer_field'], 1)
        self.assertEqual(content['new']['float_field'], 1.0)
        self.assertItemsEqual(content['changes'].keys(), keys)

    def test_content_update(self):
        model = TestModel(
            string_field='Test',
            integer_field=1,
            float_field=1.0,
        )
        old_object = serialize_model_instance(model)
        model.string_field = 'Modified'
        new_object = serialize_model_instance(model)
        keys = ['id', 'string_field', 'integer_field', 'float_field']

        content = signals._extract_content_data(old_object, new_object)

        self.assertItemsEqual(content['new'].keys(), keys)
        self.assertItemsEqual(content['old'].keys(), keys)
        self.assertEqual(content['new']['string_field'], 'Modified')
        self.assertEqual(content['old']['string_field'], 'Test')
        self.assertItemsEqual(content['changes'].keys(), ['string_field'])

    def test_content_delete(self):
        model = TestModel(
            string_field='Test',
            integer_field=1,
            float_field=1.0,
        )
        old_object = serialize_model_instance(model)
        model.string_field = None
        model.integer_field = None
        model.float_field = None
        model.id = None
        keys = ['id', 'string_field', 'integer_field', 'float_field']

        content = signals._extract_content_data(old_object, None)

        self.assertIsNone(content['new'])
        self.assertItemsEqual(content['old'].keys(), keys)
        self.assertEqual(content['old']['string_field'], 'Test')
        self.assertEqual(content['old']['integer_field'], 1)
        self.assertEqual(content['old']['float_field'], 1.0)
        self.assertItemsEqual(content['changes'].keys(), keys)

    def test_content_empty(self):
        content = signals._extract_content_data()

        self.assertIsNone(content['old'])
        self.assertIsNone(content['new'])
        self.assertEqual(content['changes'], {})

    def test_instance_data(self):
        model = TestModel()
        model.id = 1

        instance_data = signals._extract_instance_data(model)

        self.assertEqual(instance_data['id'], '1')
        self.assertEqual(instance_data['description'], '')

    def test_instance_data_wrong(self):
        model = TestModel()
        model.id = u'foo'
        model.description = 'bar'

        with patch('audit_tools.audit.signals.unicode', side_effect=ValueError):
            instance_data = signals._extract_instance_data(model)

        self.assertEqual(instance_data['id'], '')
        self.assertEqual(instance_data['description'], '')

    def test_pre_save_new(self):
        model = TestModel(
            string_field='Test',
            integer_field=1,
            float_field=1.0,
            id=1
        )
        sender = MagicMock()
        sender.objects.get.side_effect = Exception('Test Exception')

        signals._pre_save(sender, instance=model)

        self.assertEqual(signals._CACHE, {})

    @patch('audit_tools.audit.signals.serialize_model_instance')
    def test_pre_save_update(self, serialize_model_instance):
        model = TestModel(
            string_field='Test',
            integer_field=1,
            float_field=1.0,
            id=1
        )
        sender = MagicMock()
        sender.objects.get.return_value = model
        serialize_model_instance.return_value = model

        signals._pre_save(sender, instance=model)
        self.assertEqual(signals._CACHE, {id(model): model})

    @patch('audit_tools.audit.signals.logger')
    def test_pre_save_fail(self, logger):
        sender = MagicMock()

        signals._pre_save(sender)
        self.assertEqual(logger.exception.call_count, 1)

    @patch('audit_tools.audit.signals.extract_process_data')
    @patch('audit_tools.audit.signals.cache')
    @patch('audit_tools.audit.signals._extract_content_data')
    @patch('audit_tools.audit.tasks.save_model_action')
    @patch('audit_tools.audit.signals.settings')
    def test_post_save_sync(self, settings, save_model_action, extract_content_data, cache, extract_process_data):
        settings.RUN_ASYNC = False
        model = TestModel(
            string_field='Test',
            integer_field=1,
            float_field=1.0,
        )
        old_object = serialize_model_instance(model)
        with patch.dict('audit_tools.audit.signals._CACHE', {id(model): old_object}):
            model.string_field = 'Modified'
            model.integer_field = 2
            model.float_field = 2.0
            new_object = serialize_model_instance(model)
            content = signals._extract_content_data(old_object, new_object)
            extract_content_data.return_value = content

            signals._post_save(model, instance=model)

            # Check that extract process and access was done successfully
            self.assertEqual(cache.get_last_access.call_count, 1)
            self.assertEqual(cache.get_process.call_count, 1)
            self.assertEqual(extract_process_data.call_count, 1)

            # Check that was called synchronously
            self.assertEqual(save_model_action.call_count, 1)
            self.assertEqual(save_model_action.apply_async.call_count, 0)

    @patch('audit_tools.audit.signals.extract_process_data')
    @patch('audit_tools.audit.signals.cache')
    @patch('audit_tools.audit.signals._extract_content_data')
    @patch('audit_tools.audit.tasks.save_model_action')
    @patch('audit_tools.audit.signals.settings')
    def test_post_save_async(self, settings, save_model_action, extract_content_data, cache, extract_process_data):
        settings.RUN_ASYNC = True
        model = TestModel(
            string_field='Test',
            integer_field=1,
            float_field=1.0,
        )
        old_object = serialize_model_instance(model)
        with patch.dict('audit_tools.audit.signals._CACHE', {id(model): old_object}):
            model.string_field = 'Modified'
            model.integer_field = 2
            model.float_field = 2.0
            new_object = serialize_model_instance(model)
            content = signals._extract_content_data(old_object, new_object)
            extract_content_data.return_value = content

            signals._post_save(model, instance=model)

            # Check that extract process and access was done successfully
            self.assertEqual(cache.get_last_access.call_count, 1)
            self.assertEqual(cache.get_process.call_count, 1)
            self.assertEqual(extract_process_data.call_count, 1)

            # Check that was called asynchronously
            self.assertEqual(save_model_action.call_count, 0)
            self.assertEqual(save_model_action.apply_async.call_count, 1)

    @patch('audit_tools.audit.signals.extract_process_data')
    @patch('audit_tools.audit.signals.cache')
    @patch('audit_tools.audit.signals._extract_content_data')
    @patch('audit_tools.audit.tasks.save_model_action')
    @patch('audit_tools.audit.signals.settings')
    def test_post_save_not_old_data(self, settings, save_model_action, extract_content_data, cache,
                                    extract_process_data):
        settings.RUN_ASYNC = False
        model = TestModel(
            string_field='Test',
            integer_field=1,
            float_field=1.0,
        )
        old_object = serialize_model_instance(model)
        model.string_field = 'Modified'
        model.integer_field = 2
        model.float_field = 2.0
        new_object = serialize_model_instance(model)
        content = signals._extract_content_data(old_object, new_object)
        extract_content_data.return_value = content

        signals._post_save(model, instance=model)

        # Check that extract process and access was done successfully
        self.assertEqual(cache.get_last_access.call_count, 1)
        self.assertEqual(cache.get_process.call_count, 1)
        self.assertEqual(extract_process_data.call_count, 1)

        # Check that was called synchronously
        self.assertEqual(save_model_action.call_count, 1)
        self.assertEqual(save_model_action.apply_async.call_count, 0)

    @patch('audit_tools.audit.signals.logger')
    @patch('audit_tools.audit.signals.extract_process_data')
    @patch('audit_tools.audit.signals.cache')
    @patch('audit_tools.audit.signals._extract_content_data')
    @patch('audit_tools.audit.tasks.save_model_action')
    @patch('audit_tools.audit.signals.settings')
    def test_post_save_fail_save_model_action(self, settings, save_model_action, extract_content_data, cache,
                                              extract_process_data, logger):
        settings.RUN_ASYNC = False
        save_model_action.side_effect = Exception
        model = TestModel(
            string_field='Test',
            integer_field=1,
            float_field=1.0,
        )
        old_object = serialize_model_instance(model)
        model.string_field = 'Modified'
        model.integer_field = 2
        model.float_field = 2.0
        new_object = serialize_model_instance(model)
        content = signals._extract_content_data(old_object, new_object)
        extract_content_data.return_value = content

        signals._post_save(model, instance=model)

        # Check that extract process and access was done successfully
        self.assertEqual(cache.get_last_access.call_count, 1)
        self.assertEqual(cache.get_process.call_count, 1)
        self.assertEqual(extract_process_data.call_count, 1)

        # Check that save process wasn't done successfully
        self.assertEqual(logger.exception.call_count, 1)

    @patch('audit_tools.audit.signals.serialize_model_instance', side_effect=Exception)
    @patch('audit_tools.audit.signals.logger')
    def test_post_save_fail(self, logger, serialize_model_instance_mock):
        model = TestModel(
                string_field='Test',
                integer_field=1,
                float_field=1.0,
        )
        signals._post_save(model, instance=model)

        # Check that save process wasn't done successfully
        self.assertEqual(logger.exception.call_count, 1)

    @patch('audit_tools.audit.signals.extract_process_data')
    @patch('audit_tools.audit.signals.cache')
    @patch('audit_tools.audit.signals._extract_content_data')
    @patch('audit_tools.audit.tasks.save_model_action')
    @patch('audit_tools.audit.signals.settings')
    def test_pre_delete_sync(self, settings, save_model_action, extract_content_data, cache, extract_process_data):
        settings.RUN_ASYNC = False
        model = TestModel(
            string_field='Test',
            integer_field=1,
            float_field=1.0,
        )
        old_object = serialize_model_instance(model)
        model.string_field = None
        model.integer_field = None
        model.float_field = None
        model.id = None
        new_object = serialize_model_instance(model)
        content = signals._extract_content_data(old_object, new_object)
        extract_content_data.return_value = content

        signals._pre_delete(model, instance=model)

        # Check that extract process and access was done successfully
        self.assertEqual(cache.get_last_access.call_count, 1)
        self.assertEqual(cache.get_process.call_count, 1)
        self.assertEqual(extract_process_data.call_count, 1)

        # Check that was called synchronously
        self.assertEqual(save_model_action.call_count, 1)
        self.assertEqual(save_model_action.apply_async.call_count, 0)

    @patch('audit_tools.audit.signals.extract_process_data')
    @patch('audit_tools.audit.signals.cache')
    @patch('audit_tools.audit.signals._extract_content_data')
    @patch('audit_tools.audit.tasks.save_model_action')
    @patch('audit_tools.audit.signals.settings')
    def test_pre_delete_async(self, settings, save_model_action, extract_content_data, cache, extract_process_data):
        settings.RUN_ASYNC = True
        model = TestModel(
            string_field='Test',
            integer_field=1,
            float_field=1.0,
        )
        old_object = serialize_model_instance(model)
        model.string_field = None
        model.integer_field = None
        model.float_field = None
        model.id = None
        new_object = serialize_model_instance(model)
        content = signals._extract_content_data(old_object, new_object)
        extract_content_data.return_value = content

        signals._pre_delete(model, instance=model)

        # Check that extract process and access was done successfully
        self.assertEqual(cache.get_last_access.call_count, 1)
        self.assertEqual(cache.get_process.call_count, 1)
        self.assertEqual(extract_process_data.call_count, 1)

        # Check that was called asynchronously
        self.assertEqual(save_model_action.call_count, 0)
        self.assertEqual(save_model_action.apply_async.call_count, 1)

    @patch('audit_tools.audit.signals.logger')
    @patch('audit_tools.audit.signals.extract_process_data')
    @patch('audit_tools.audit.signals.cache')
    @patch('audit_tools.audit.signals._extract_content_data')
    @patch('audit_tools.audit.tasks.save_model_action', side_effect=Exception)
    @patch('audit_tools.audit.signals.settings')
    def test_pre_delete_fail_save_model_action(self, settings, save_model_action, extract_content_data, cache,
                                               extract_process_data, logger):
        settings.RUN_ASYNC = False
        model = TestModel(
            string_field='Test',
            integer_field=1,
            float_field=1.0,
        )
        content = signals._extract_content_data()
        extract_content_data.return_value = content

        signals._pre_delete(model, instance=model)

        # Check that extract process and access was done successfully
        self.assertEqual(cache.get_last_access.call_count, 1)
        self.assertEqual(cache.get_process.call_count, 1)
        self.assertEqual(extract_process_data.call_count, 1)

        # Check that save process wasn't done successfully
        self.assertEqual(logger.exception.call_count, 1)

    @patch('audit_tools.audit.signals.logger')
    @patch('audit_tools.audit.signals.serialize_model_instance', side_effect=Exception)
    def test_pre_delete_fail(self, serialize_model_instance_mock, logger):
        model = TestModel(
            string_field='Test',
            integer_field=1,
            float_field=1.0,
        )

        signals._pre_delete(model, instance=model)

        # Check that save process wasn't done successfully
        self.assertEqual(logger.exception.call_count, 1)

    @patch('audit_tools.audit.signals.dynamic_import', return_value=None)
    @patch('audit_tools.audit.signals.logger')
    @patch('audit_tools.audit.signals.pre_save')
    @patch('audit_tools.audit.signals.post_save')
    @patch('audit_tools.audit.signals.pre_delete')
    @patch('audit_tools.audit.signals.settings')
    def test_register_fail(self, settings, pre_delete, post_save, pre_save, logger, dynamic_import):
        settings.LOGGED_MODELS = ('audit_tools.audit.tests.TestClass', )
        pre_save.connect.side_effect = Exception('TestException')

        signals.register_models()

        self.assertEqual(logger.error.call_count, 1)

    @patch('audit_tools.audit.signals.dynamic_import', return_value=None)
    @patch('audit_tools.audit.signals.logger')
    @patch('audit_tools.audit.signals.pre_save')
    @patch('audit_tools.audit.signals.post_save')
    @patch('audit_tools.audit.signals.pre_delete')
    @patch('audit_tools.audit.signals.settings')
    def test_register_ok(self, settings, pre_delete, post_save, pre_save, logger, dynamic_import):
        settings.LOGGED_MODELS = ('audit_tools.audit.fail.FailClass', )

        signals.register_models()

        self.assertEqual(pre_save.connect.call_count, 1)
        self.assertEqual(post_save.connect.call_count, 1)
        self.assertEqual(pre_delete.connect.call_count, 1)
        self.assertEqual(logger.error.call_count, 0)

    @patch('audit_tools.audit.signals.dynamic_import', return_value=None)
    @patch('audit_tools.audit.signals.logger')
    @patch('audit_tools.audit.signals.pre_save')
    @patch('audit_tools.audit.signals.post_save')
    @patch('audit_tools.audit.signals.pre_delete')
    @patch('audit_tools.audit.signals.settings')
    def test_unregister_fail(self, settings, pre_delete, post_save, pre_save, logger, dynamic_import):
        settings.LOGGED_MODELS = ('audit_tools.audit.tests.TestClass', )
        pre_save.disconnect.side_effect = Exception('Test Exception')

        signals.unregister_models()

        self.assertEqual(logger.error.call_count, 1)

    @patch('audit_tools.audit.signals.dynamic_import', return_value=None)
    @patch('audit_tools.audit.signals.logger')
    @patch('audit_tools.audit.signals.pre_save')
    @patch('audit_tools.audit.signals.post_save')
    @patch('audit_tools.audit.signals.pre_delete')
    @patch('audit_tools.audit.signals.settings')
    def test_unregister_ok(self, settings, pre_delete, post_save, pre_save, logger, dynamic_import):
        settings.LOGGED_MODELS = ('audit_tools.audit.fail.FailClass', )

        signals.unregister_models()

        self.assertEqual(pre_save.disconnect.call_count, 1)
        self.assertEqual(post_save.disconnect.call_count, 1)
        self.assertEqual(pre_delete.disconnect.call_count, 1)
        self.assertEqual(logger.error.call_count, 0)

    def tearDown(self):
        pass