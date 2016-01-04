from __future__ import unicode_literals
from rest_framework import permissions

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
                name='audit',
                model='audit'
            )
            logger.warn('Content type registered yet: audit')
        except ContentType.DoesNotExist:
            model_action_content_type = ContentType.objects.create(
                app_label='audit',
                name='audit',
                model='audit'
            )

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
        content_type = ContentType.objects.get(app_label='audit', name='audit', model='audit')
        Permission.objects.filter(content_type=content_type).delete()
        ContentType.objects.filter(app_label='audit', name='audit', model='audit').delete()
    except ContentType.DoesNotExist:
        logger.exception("Audit isn't registered")
        return False

    return True


class SearchAccess(permissions.BasePermission):
    """
    Global permission check for Search accesses.
    """

    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated() and user.has_perm('audit.search'):
            return True

        return False


class APIAccess(permissions.BasePermission):
    """
    Global permission check for API accesses.
    """

    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated() and user.has_perm('audit.api'):
            return True

        return False
