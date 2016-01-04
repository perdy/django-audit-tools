from __future__ import unicode_literals

import logging

from djcelery.app import app
from mongoengine import ValidationError

from audit import settings

logger = logging.getLogger(__name__)


@app.task(queue=settings.CELERY_QUEUE)
def save_access(access):
    try:
        logger.debug("Pre save access")
        access.save()
        logger.debug("Post save access: %s", access.id)
    except:
        logger.exception("Error saving Access document")

    return True


@app.task(queue=settings.CELERY_QUEUE)
def save_model_action(model_action_data, access, process):
    from audit.models import Access
    from audit.models.models_factory import create_model_action
    try:
        logger.debug("Pre save ModelAction")
        try:
            a = Access.objects.get(id=access.id)
            m = create_model_action(model_action_data, a, process)
        except AttributeError:
            m = create_model_action(model_action_data, None, process)
        except ValidationError:
            access.save()
            a = Access.objects.get(id=access.id)
            m = create_model_action(model_action_data, a, process)
        m.save()
        logger.debug("Post save ModelAction: %s", m.id)
    except:
        logger.exception("Error saving ModelAction document")

    return True
