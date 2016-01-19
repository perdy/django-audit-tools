# -*- encoding: utf-8 -*-
"""
Module with some factory methods for models.
"""
from __future__ import unicode_literals

import datetime

from audit_tools.audit.cache import cache

__all__ = ['create_access', 'create_model_action', 'update_access']


def create_model_action(model_action_data, access, process):
    """
    Create an instance of :class:`audit_tools.ModelAction` given a dict of his field values and an access and process.

    :param model_action_data: Model fields values.
    :type model_action_data: dict
    :param access: Access linked to model action.
    :type access: :class:`audit_tools.Access`
    :param process: Process linked to model action.
    :type process: :class:`audit_tools.Process`
    :return: Model action created.
    :rtype: :class:`audit_tools.ModelAction`
    """
    model_action_data['access'] = access
    model_action_data['process'] = process
    model_action = _model_action_factory(**model_action_data)

    return model_action


def create_access(access, process):
    """
    Create an instance of :class:`audit_tools.Access` given a dict of his field values and a process.

    :param access: Access field values.
    :type access: dict
    :param process: Process field values.
    :type process: dict
    :return: Access created.
    :rtype: :class:`audit_tools.Access`
    """
    p = cache.get_process(process)

    access['process'] = p
    a = _access_factory(**access)

    return a


def update_access(access, **update_data):
    """
    Update an :class:`audit_tools.Access` object.

    :param access: Access object.
    :type access: :class:`audit_tools.Access`
    :param update_data: New field values for this object.
    :type update_data: dict
    :return: Access object updated.
    :rtype: :class:`audit_tools.Access`
    """
    from audit_tools.audit.models.access import AccessRequest, AccessTime, AccessView, AccessResponse, \
        AccessException, AccessUser
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
    """
    Factory to create :class:`audit_tools.ModelAction` in a flexible way. The object is not stored.

    :param model: Objective model field values.
    :type model: dict
    :param action: Action performed.
    :type action: str
    :param content: Object content changes.
    :type content: dict
    :param instance: Objective instance field values.
    :type instance: dict
    :param timestamp: Timestamp.
    :type timestamp: :class:`datetime.datetime`
    :param process: Process linked.
    :type process: :class:`audit_tools.Process`
    :param access: Access linked.
    :type access: :class:`audit_tools.Access`
    :return: Model created.
    :rtype: :class:`audit_tools.ModelAction`
    """
    from audit_tools.audit.models.model_action import ModelActionModel, ModelActionContent, ModelActionInstance, \
        ModelAction

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
    """
    Factory to create :class:`audit_tools.Access` in a flexible way. The object is not stored.

    :param request: Request.
    :type request: :class:`audit_tools.AccessRequest`
    :param time: Request and response times.
    :type time: dict
    :param view: Django view called (name, app, full_name, args and kwargs).
    :type view: dict
    :param response: Response to user (content, type and status_code).
    :type response: dict
    :param exception: Exception (type, message and trace) if raised.
    :type exception: dict
    :param process: Process linked.
    :type process: :class:`audit_tools.Process`
    :param user: User (id and username) that performed the request.
    :type user: dict
    :param custom: Custom data.
    :type custom: dict
    :param interlink_id: Interlink id.
    :type interlink_id: str
    :return: Access created.
    :rtype: :class:`audit_tools.Access`
    """
    from audit_tools.audit.models.access import AccessResponse, AccessTime, AccessView, AccessUser, AccessException, \
        Access

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
