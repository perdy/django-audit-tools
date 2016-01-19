from __future__ import unicode_literals

import datetime
import re
import itertools
import traceback
import logging

from bson.json_util import loads

from audit_tools.audit.cache import cache
from audit_tools.audit.decorators import CheckActivate
from audit_tools.audit import settings
from audit_tools.audit.tasks import save_access
from audit_tools.audit.models.models_factory import create_access, update_access
from audit_tools.audit.utils import request_to_dict, import_providers, extract_process_data, fix_dict

try:
    from ebury_interlink.cache import get_access_interlink_id
except ImportError:
    get_access_interlink_id = lambda: None

logger = logging.getLogger(__name__)


class AuditMiddleware(object):
    """Middleware for audit logging
    """

    def __init__(self, *args, **kwargs):
        # Attributes
        self._blacklisted = False
        self._disabled = False
        self._view = {}
        self._time = {}
        self._user = None
        self._process = None
        self._access = None
        self._response = {}
        self._exception = {}

        # Dynamic import of provider functions
        self._providers = import_providers()

    @CheckActivate
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Preprocess request.

        :param request: Http request.
        :type request: django.http.HttpRequest
        :param view_func: View.
        :type view_func: callable
        :param view_args: View arguments.
        :type view_args: list
        :param view_kwargs: View keyword arguments.
        :type view_kwargs: dict
        :return: None
        """
        self._disabled = getattr(view_func, 'disable_audit', False)

        if not self._disabled:
            try:
                view_data = self._extract_view_data(view_func, view_args, view_kwargs)

                self._blacklisted = self._check_blacklist(request.path, view_data['app'])

                msg = "<Process View> View:%s %s", view_data['full_name'], 'BlackList' if self._blacklisted else ''
                logger.debug(msg)

                if not self._blacklisted:
                    self._view = view_data
                    user = self._extract_user_data(request)

                    # Time
                    self._time = {
                        'request': datetime.datetime.now(),
                        'response': None
                    }

                    # Interlink ID
                    interlink_id = get_access_interlink_id()

                    # Create access
                    access = {
                        'interlink_id': interlink_id,
                        'request': request_to_dict(request),
                        'response': None,
                        'time': self._time,
                        'view': self._view,
                        'user': user,
                        'custom': None,
                    }

                    # Extract process data
                    self._process = extract_process_data()

                    # Save Access
                    self._access = create_access(access, self._process)
                    cache.set_last_access(self._access)

                    if not settings.RUN_ASYNC:
                        save_access(self._access)
                    else:
                        save_access.apply_async((self._access, ))
                    logger.info("<Process View> View:%s", self._view['full_name'])

                    logger.debug("View:%s", str(self._view))
            except Exception:
                logger.exception("<Process View>")

        return None

    @CheckActivate
    def process_response(self, request, response):
        """Postprocess response.

        :param request: Http request.
        :type request: django.http.HttpRequest
        :param response: Response.
        :type response: django.http.HttpResponse
        :return: None
        """
        try:
            if self._blacklisted:
                logger.debug("<Process Response> View:%s %s", str(self._view), 'BlackList')
            elif self._disabled:
                logger.debug("<Process Response> View:%s %s", str(self._view), 'Disabled')
            else:
                logger.debug("<Process Response> View:%s", str(self._view))

            if not self._blacklisted and not self._disabled:
                # Response
                self._response = self._extract_response_data(response)

                # Time
                self._time['response'] = datetime.datetime.now()

                # Providers
                custom = {app: f(request) for app, f in self._providers.iteritems()}
                custom = {k: v for k, v in custom.iteritems() if v is not None and len(v) > 0}

                # Save Access and Process
                self._access = update_access(self._access, response=self._response, time=self._time, custom=custom)

                if not settings.RUN_ASYNC:
                    save_access(self._access)
                else:
                    save_access.apply_async((self._access, ))
                logger.info("<Process Response> View:%s", self._view['full_name'])
        except Exception:
            logger.exception("<Process Response>")

        return response

    @CheckActivate
    def process_exception(self, request, exception):
        """Postprocess exception.

        :param request: Http request.
        :type request: django.http.HttpRequest
        :param exception: Response.
        :type exception: Exception
        :return: None
        """
        try:
            if self._blacklisted:
                logger.debug("<Process Exception> View:%s %s", str(self._view), 'BlackList')
            elif self._disabled:
                logger.debug("<Process Exception> View:%s %s", str(self._view), 'Disabled')
            else:
                logger.debug("<Process Exception> View:%s", str(self._view))

            if not self._blacklisted and not self._disabled:
                # Time
                self._time['response'] = datetime.datetime.now()

                # Providers
                custom = {app: f(request) for app, f in self._providers.iteritems()}
                custom = {k: v for k, v in custom.iteritems() if v is not None and len(v) > 0}

                self._exception = self._extract_exception_data(exception)

                # Save Access and Process
                self._access = update_access(self._access, time=self._time, custom=custom, exception=self._exception)

                if not settings.RUN_ASYNC:
                    save_access(self._access)
                else:
                    save_access.apply_async((self._access, ))
                logger.info("<Process Exception> View:%s Message:%s", self._view['full_name'], exception.message)
        except Exception:
            logger.exception("<Process Exception>")

        return None

    def _check_blacklist(self, path, app=''):
        """Check if path is blacklisted according to BLACKLIST variable in settings.

        :param path: URL path.
        :type path: str
        :param app: App.
        :type app: str
        :return: True if blacklisted.
        :rtype: bool
        """
        blacklisted = False

        if app in settings.BLACKLIST:
            regexs = itertools.chain(settings.BLACKLIST[app], settings.BLACKLIST.get('', ()))
        else:
            regexs = settings.BLACKLIST.get('', ())

        for regex in (r for r in regexs if not blacklisted):
            r = re.compile(r'({})'.format(regex))
            s = r.search(path)
            blacklisted = s is not None and (len(s.groups()) > 0)

        return blacklisted

    def _extract_view_data(self, view_func, view_args, view_kwargs):
        """Extract view data that will be stored in Access model.

        :param view_func: Function or method that act as a Django view.
        :type view_func: function
        :param view_args: View args.
        :type view_args: list
        :param view_kwargs: View kwargs.
        :type view_kwargs: dict
        :return: Extracted data.
        :rtype: dict
        """
        try:
            name = view_func.__self__.__class__.__name__
        except AttributeError:
            name = view_func.__name__

        full_name = view_func.__module__ + '.' + name
        app = full_name.split('.', 1)[0]

        return {
            'full_name': full_name,
            'app': app,
            'name': name,
            'args': view_args,
            'kwargs': view_kwargs,
        }

    def _extract_user_data(self, request):
        """Extract user data from a request.

        :param request: Django request.
        :type request: django.http.HttpRequest
        :return: Extracted data.
        :rtype: dict
        """
        try:
            user_id = request.user.id or -1
            user_username = request.user.username or 'Anonymous'
        except:
            user_id = -1
            user_username = 'Anonymous'

        return {
            'id': user_id,
            'username': user_username,
        }

    def _extract_response_data(self, response):
        """Extract response data.

        :param response: Django http response object.
        :type response: django.http.HttpResponse
        :return: Extracted data.
        :rtype: dict
        """
        try:
            content_type = response.get('Content-Type', '')
            ct = content_type.lower()

            if 'json' in ct:
                response_content = loads(response._container[0])
            elif 'xml' in ct:
                response_content = response._container[0].decode('utf-8', errors='ignore')
            else:
                response_content = None
        except:
            response_content = None

        return {
            'content': fix_dict(response_content),
            'type': response.get('Content-Type', ''),
            'status_code': response.status_code,
            }

    def _extract_exception_data(self, exception):
        """Extract exception data.

        :param exception: Exception object.
        :type exception: Exception
        :return: Extracted data.
        :rtype: dict
        """
        return {
            'type': exception.__class__.__name__,
            'message': unicode(exception.message),
            'trace': traceback.format_exc(),
            }


def custom_provider(*args, **kwargs):
    """Custom provider default function.

    :return: {}
    """
    return {}  # pragma: no cover
