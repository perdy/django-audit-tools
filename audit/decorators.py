from __future__ import unicode_literals
"""Audit decorators"""

import functools

from audit import settings


class CheckActivate(object):
    """Decorator that check if audit is activated or deactivated.

    :param func: Function to decorate.
    """

    def __init__(self, func, *args, **kwargs):
        self.func = func
        functools.update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        if settings.ACTIVATE:
            return self.func(*args, **kwargs)

        res = None if self.func.__name__ != 'process_response' else args[2]
        return res

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self.func
        return functools.partial(self, obj)


class DisableAudit(object):
    """Decorator for activate or deactivate audit in a view.

    :param func: Function to decorate.
    """

    def __init__(self, func, *args, **kwargs):
        func.disable_audit = True
        self.func = func
        functools.update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self.func
        return functools.partial(self, obj)
