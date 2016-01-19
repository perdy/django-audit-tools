# -*- encoding: utf-8 -*-
"""
Module that defines an internal cache for managing processes and accesses through threads.
"""
from __future__ import unicode_literals

import threading

from mongoengine import DoesNotExist

__all__ = ['cache']

THREAD_NAMESPACE = threading.local()


class Cache(object):
    """
    Cache object to hold audit object through thread memory space.
    """
    def __init__(self):
        """
        Create Cache object and get thread namespace.
        """
        self.namespace = THREAD_NAMESPACE

    def get_process(self, process):
        """
        Get current process. If not exists, create it.

        :param process: Process data.
        :type process: dict.
        :return: Process
        :rtype: :class:`audit_tools.audit.Process`
        """
        from audit_tools.audit.models import Process

        p = getattr(self.namespace, "audit_current_process", None)
        if p is None:
            try:
                p = Process.objects.get(pid=process['pid'], machine=process['machine'],
                                        creation_time=process['creation_time'])
            except DoesNotExist:
                p = Process(**process)
                p.save()

            self.set_process(p)

        return p

    def set_process(self, process):
        """
        Set current process.

        :param process: Process object:
        :type process: :class:`audit_tools.audit.Process`
        """
        self.namespace.audit_current_process = process

    def get_last_access(self):
        """
        Get last access. If there is not access, none will be returned.

        :return: Last access or None if there is not access.
        :rtype: :class:`audit_tools.audit.Access`
        """
        a = getattr(self.namespace, "audit_current_access", None)

        return a

    def set_last_access(self, access):
        """
        Set last access.

        :param access: Access object.
        :type access: :class:`audit_tools.audit.Access`
        """
        self.namespace.audit_current_access = access

cache = Cache()
