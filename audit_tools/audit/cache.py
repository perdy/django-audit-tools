# -*- encoding: utf-8 -*-
"""
Module that defines an internal cache for managing processes and accesses through threads.
"""
from __future__ import unicode_literals

import threading

from mongoengine import DoesNotExist

__all__ = ['THREAD_NAMESPACE', 'get_process', 'set_process', 'get_last_access', 'set_last_access']

THREAD_NAMESPACE = threading.local()


def get_process(process):
    from audit_tools.audit.models import Process

    if hasattr(THREAD_NAMESPACE, "audit_current_process"):
        p = THREAD_NAMESPACE.audit_current_process
    else:
        try:
            p = Process.objects.get(
                pid=process['pid'],
                machine=process['machine'],
                creation_time=process['creation_time']
            )
        except DoesNotExist:
            p = Process(**process)
            p.save()
            
        set_process(p)

    return p


def set_process(process):
    THREAD_NAMESPACE.audit_current_process = process


def get_last_access():
    if hasattr(THREAD_NAMESPACE, "audit_current_access"):
        a = THREAD_NAMESPACE.audit_current_access
    else:
        a = None

    return a


def set_last_access(access):
    THREAD_NAMESPACE.audit_current_access = access
