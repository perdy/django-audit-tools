from __future__ import unicode_literals
"""
This module implements permissions in audit using default database of django
"""

import logging

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


logger = logging.getLogger(__name__)

AUDIT_PERMISSIONS = (
    ('search', 'Can access to Audit search interface'),
    ('api', 'Can access to Audit API')
)


def register_permissions():
    """
    Method to register permissions in database
    """
    try:
        try:
            model_action_content_type = ContentType.objects.get(
                app_label='audit',
                name='model action',
                model='modelaction'
            )
            logger.warn('Content type registered yet: audit modelaction')
        except ContentType.DoesNotExist:
            model_action_content_type = ContentType(
                app_label='audit',
                name='model action',
                model='modelaction'
            )
            model_action_content_type.save()

        for permission_code, permission_name in AUDIT_PERMISSIONS:
            try:
                Permission.objects.get(
                    content_type=model_action_content_type,
                    codename=permission_code,
                    name=permission_name
                )
                logger.warn('Permission registered yet: {}'.format(permission_code))
            except Permission.DoesNotExist:
                permission = Permission(
                    content_type=model_action_content_type,
                    codename=permission_code,
                    name=permission_name
                )
                permission.save()
    except Exception:
        logger.exception("Error registering permissions")
        return False

    return True


def unregister_permissions():
    """
    Method to unregister permissions in database
    """
    try:
        content_type = ContentType.objects.get(app_label='audit', name='model action', model='modelaction')
        Permission.objects.filter(content_type=content_type).delete()
        ContentType.objects.filter(app_label='audit', name='model action', model='modelaction').delete()
    except ContentType.DoesNotExist as ex:
        logger.exception(ex.message)
        return False

    return True
