from __future__ import unicode_literals

import datetime
import logging

from django.db.models.signals import pre_save, post_save, pre_delete
from audit.cache import get_process, get_last_access
from audit.decorators import CheckActivate

from audit import settings
from audit.tasks import save_model_action
from audit.models.models_factory import create_model_action
from audit.utils import extract_process_data, dynamic_import, serialize_model_instance


_CACHE = {}

logger = logging.getLogger(__name__)


@CheckActivate
def _pre_save(sender, **kwargs):
    try:
        i = kwargs['instance']
        if i.pk:
            try:
                original_instance = sender.objects.get(pk=i.pk)
                _CACHE[id(i)] = serialize_model_instance(original_instance)
            except:
                # New object.
                pass
    except:
        logger.exception("<Pre Save>")


@CheckActivate
def _post_save(sender, **kwargs):
    try:
        from audit.models import ACTIONS

        i = kwargs['instance']

        # Model
        model_module = i.__module__
        model_name = i.__class__.__name__
        model = {
            'app': model_module.split('.', 1)[0],
            'full_name': model_module + '.' + model_name,
            'name': model_name,
        }

        # Old and new content
        old_data = {}
        if id(i) in _CACHE:
            old_data = _CACHE[id(i)]
            del _CACHE[id(i)]
        new_data = serialize_model_instance(i)
        content = {
            'old': old_data,
            'new': new_data,
        }

        # Action
        if not old_data and new_data:
            action = ACTIONS.CREATE
            content['changes'] = {k: {'old': None, 'new': v} for k, v in new_data.iteritems()}
        else:
            content['changes'] = {
                k1: {'old': v1, 'new': v2}
                for k1, v1 in old_data.iteritems()
                for k2, v2 in new_data.iteritems()
                if k1 == k2 and v1 != v2
            }
            action = ACTIONS.UPDATE

        # Instance
        instance = {
            'id': unicode(i.pk),
            'description': unicode(i),
        }

        # Timestamp
        timestamp = datetime.datetime.now()

        model_action = {
            'model': model,
            'action': action,
            'content': content,
            'instance': instance,
            'timestamp': timestamp,
        }

        # Process
        process = extract_process_data()

        try:
            # Get process
            process = get_process(process)
            access = get_last_access()

            if not settings.RUN_ASYNC:
                save_model_action(model_action, access, process)
            else:
                save_model_action.apply_async((model_action, access, process))
            logger.info("<%s> Model:%s ID:%s", action.capitalize(), model['full_name'], instance['id'])
        except:
            logger.exception("<%s> Model:%s ID:%s %s", action.capitalize(), model['full_name'], instance['id'])
    except:
        logger.exception("<Post Save>")


@CheckActivate
def _pre_delete(sender, **kwargs):
    try:
        from audit.models import ACTIONS

        i = kwargs['instance']

        # Model
        model_module = i.__module__
        model_name = i.__class__.__name__
        model = {
            'app': model_module.split('.', 1)[0],
            'full_name': model_module + '.' + model_name,
            'name': model_name,
        }

        # Old and new content
        old_data = serialize_model_instance(i)
        new_data = {}
        content = {
            'old': old_data,
            'new': new_data,
            'changes': {k: {'old': v, 'new': None} for k, v in old_data.iteritems()}
        }

        # Action
        action = ACTIONS.DELETE

        # Instance
        instance = {
            'id': unicode(i.pk),
            'description': unicode(i),
        }

        # Timestamp
        timestamp = datetime.datetime.now()

        model_action = {
            'model': model,
            'action': action,
            'content': content,
            'instance': instance,
            'timestamp': timestamp,
        }

        # Process
        process = extract_process_data()

        try:
            # Get process
            process = get_process(process)
            access = get_last_access()

            if not settings.RUN_ASYNC:
                save_model_action(model_action, access, process)
            else:
                save_model_action.apply_async((model_action, access, process))

            logger.info("<%s> Model:%s ID:%s", action.capitalize(), model['full_name'], instance['id'])
        except:
            logger.exception("<%s> Model:%s ID:%s Error:%s", action.capitalize(), model['full_name'], instance['id'])
    except:
        logger.exception("<Pre Delete> %s")


def register(model):
    """Register a model to the audit code.

    :param model: Model to register.
    :type model: object
    """
    try:
        pre_save.connect(_pre_save, sender=model, dispatch_uid=str(model))
        post_save.connect(_post_save, sender=model, dispatch_uid=str(model))
        pre_delete.connect(_pre_delete, sender=model, dispatch_uid=str(model))
    except Exception as e:
        logger.error("<Register> %s", e.message)


def unregister(model):
    """Unregister a model to the audit code.

    :param model: Model to unregister.
    :type model: object
    """
    try:
        pre_save.disconnect(_pre_save, sender=model, dispatch_uid=str(model))
        post_save.disconnect(_post_save, sender=model, dispatch_uid=str(model))
        pre_delete.disconnect(_pre_delete, sender=model, dispatch_uid=str(model))
    except Exception as e:
        logger.error("<Unregister> %s", e.message)


def register_models():
    """Register all models listed in :const:`settings.LOGGED_MODELS`.
    """

    for model in settings.LOGGED_MODELS:
        m = dynamic_import(model)
        register(m)


def unregister_models():
    """Unregister all models listed in :const:`settings.LOGGED_MODELS`.
    """
    for model in settings.LOGGED_MODELS:
        m = dynamic_import(model)
        unregister(m)