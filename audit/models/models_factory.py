# -*- encoding: utf-8 -*-
"""
Module with some factory methods for models.
"""
from __future__ import unicode_literals
import datetime

from audit.cache import get_process

__all__ = ['create_access', 'create_model_action', 'update_access']


def create_model_action(model_action_data, access, process):
    # Store model_action
    model_action_data['access'] = access
    model_action_data['process'] = process
    model_action = _model_action_factory(**model_action_data)

    return model_action


def create_access(access, process):
    p = get_process(process)

    # Store access
    access['process'] = p
    a = _access_factory(**access)

    return a


def update_access(access, **update_data):
    from audit.models.access import AccessRequest, AccessTime, AccessView, AccessResponse, AccessException, \
        AccessUser
    if 'request' in update_data:
        access.request = AccessRequest(**update_data['request'])
    if 'time' in update_data:
        access.time = AccessTime(**update_data['time'])
    if 'view' in update_data:
        access.view = AccessView(**update_data['view'])
    if 'response' in update_data:
        access.response = AccessResponse(**update_data['response'])
    if 'exception' in update_data:
        access.exception = AccessException(**update_data['exception'])
    if 'process' in update_data:
        access.process = update_data['process']
    if 'user' in update_data:
        access.user = AccessUser(**update_data['user'])
    if 'custom' in update_data:
        access.custom = update_data['custom']

    return access


def _model_action_factory(model, action, content, instance, timestamp=datetime.datetime.now(), process=None,
                          access=None):
    from audit.models.model_action import ModelActionModel, ModelActionContent, ModelActionInstance, ModelAction

    model_document = ModelActionModel(**model)
    content_document = ModelActionContent(**content)
    instance_document = ModelActionInstance(**instance)

    model_action = ModelAction(
        model=model_document,
        action=action,
        content=content_document,
        instance=instance_document,
        timestamp=timestamp,
        access=access,
        process=process,
    )

    return model_action


def _access_factory(request, time, view, response=None, exception=None, process=None, user=None, custom=None,
                    interlink_id=None):
    from audit.models.access import AccessResponse, AccessTime, AccessView, AccessUser, AccessException, Access

    exception_document = AccessException(**exception) if exception else None
    response_document = AccessResponse(**response) if response else None
    time_document = AccessTime(**time)
    view_document = AccessView(**view)
    user_document = AccessUser(**user) if user else None

    access = Access(
        interlink_id=interlink_id,
        request=request,
        response=response_document,
        exception=exception_document,
        time=time_document,
        view=view_document,
        user=user_document,
        custom=custom,
        process=process,
    )

    return access

