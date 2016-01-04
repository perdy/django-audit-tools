from __future__ import unicode_literals
import os
import re
import socket
import datetime
import sys
import importlib
import decimal
import logging
import unicodedata

import psutil
from bson.json_util import loads

from django.db.models.fields.files import FieldFile
from django.forms import model_to_dict
from django.utils.translation import ugettext_lazy

from audit import settings


try:
    from ebury_interlink.cache import get_process_interlink_id
except ImportError:
    get_process_interlink_id = lambda: None


LOG = logging.getLogger(__name__)


def dynamic_import(callable_str):
    """Import a callable from his full name string (app.module.callable).

    :param callable_str: Full name string (app.module.callable).
    :type callable_str: str
    :return: Callable imported.
    :rtype: object
    """
    callable_mod_name, callable_name = callable_str.rsplit('.', 1)
    callable_mod = importlib.import_module(callable_mod_name)
    c = getattr(callable_mod, callable_name)

    return c


def filter_request_meta(meta):
    """Filter all entries in request metadata that are part of os environ.

    :param meta: request metadata
    :type meta: dict
    :return: Filtered request metadata
    :rtype: dict
    """
    return {k: v for k, v in meta.iteritems() if k not in os.environ.keys()}


def parse_request_meta(meta):
    """Parses request metadata from string or dict.

    :param meta: request.META
    :type meta: str
    :return: Parsed request metadata
    :rtype: dict
    :raise: ValueError
    """
    metadata = meta
    # Escape double quotes
    meta = unicode(metadata)
    meta = meta.replace(r'"', r'\"')
    meta = re.sub(r'\\"(.*?)\'(.*?)\'(.*?)\\"', r"""'\1\\"\2\\"\3'""", meta)
    # Change single quote with double quote
    meta = re.sub(r"u?\'(.*?)\'", r'"\1"', meta)
    # Remove TERMCAP and LS_COLORS fields
    meta = re.sub(r'"TERMCAP": ".*?",\n', "", meta, re.DOTALL)
    meta = re.sub(r'"LS_COLORS": ".*?",\n', "", meta, re.DOTALL)
    # Change tuples () with lists []
    meta = re.sub(r": \((.+?,.*?)\)", r": [\1]", meta)
    # Change objects <> with empty strings ""
    meta = re.sub(r"<(\w+)(.*?)>(,|\})", r'"<\1>"\3', meta)
    # False and True to lowercase
    meta = meta.replace("False", "false")
    meta = meta.replace("True", "true")
    # Change points . with underscores _ in keys
    meta = re.sub(r'(".+?":)(.+?(,|\}))', lambda m: m.group(1).replace(".", "_") + m.group(2), meta)
    # Parse json
    meta_dict = loads(meta)

    return filter_request_meta(meta_dict)


def fix_dict(dictionary, force_str=False):
    """Fix dictionary keys to make compatible with JSON, removing '.' and '$' characters.
    Fix dictionary values, doing a str over each value.

    :param dictionary: Dictionary to be fixed.
    :type dictionary: dict
    :return: Dictionary fixed.
    :rtype: dict
    """
    if isinstance(dictionary, dict):
        fix_key = lambda s: s.replace('.', '_').replace('$', '_')
        fix_value = lambda v: unicode(v) if force_str else v
        return {fix_key(k): fix_value(v) for k, v in dictionary.iteritems()}
    else:
        return dictionary


def request_to_dict(request):
    """Convert a Django request object to python dict that contains all object's fields.

    :param request: Django request object.
    :type request: django.http.HttpRequest
    :return: Request as a python dictionary.
    :rtype: dict
    """
    d = {
        'path': str(request.path),
        'GET': fix_dict(querydict_to_dict(request.GET), force_str=True),
        'POST': fix_dict(querydict_to_dict(request.POST), force_str=True),
        'COOKIES': fix_dict(request.COOKIES, force_str=True),
        'METADATA': None,
        'RAW_METADATA': None,
    }

    try:
        metadata = fix_dict(filter_request_meta(request.META), force_str=True)
        d['METADATA'] = metadata
    except ValueError as e:
        LOG.warning("<Parse METADATA> {}\n{}".format(e.message, str(request.META)))
        d['RAW_METADATA'] = str(request.META)
    return d


def querydict_to_dict(querydict):
    """Convert a QueryDict item to python dict.

    :param querydict: QueryDict.
    :type querydict: QueryDict
    :return: Python dict.
    :rtype: dict
    """
    data = {}
    for key, value in querydict.items():
        data[key] = value
    return data


def import_providers():
    """Import all provider functions.

    :return: Dictionary with all providers as: {app_name: provider_function}
    :rtype: dict
    """
    providers = {}
    for app, provider in settings.CUSTOM_PROVIDER.iteritems():
        providers[app] = dynamic_import(provider)

    return providers


def _adapt(obj):
    """Adapt incompatible objects to BSON. Returns unmodified object if compatible.

    :param obj: Object to convert.
    :return: Adapted object.
    :rtype: object
    """
    if isinstance(obj, datetime.date):
        return datetime.datetime(year=obj.year, month=obj.month, day=obj.day)

    if isinstance(obj, datetime.time):
        return datetime.datetime.combine(datetime.datetime(1, 1, 1), obj)

    if isinstance(obj, decimal.Decimal):
        return float(obj)

    if isinstance(obj, str):
        return unicodedata.normalize('NFKD', obj.decode('utf-8', 'ignore')).\
            encode('ascii', "ignore").decode('utf-8', errors='ignore')

    if isinstance(obj, unicode):
        return unicodedata.normalize('NFKD', obj).encode('ascii', "ignore").decode('utf-8', errors='ignore')

    if isinstance(obj, FieldFile):
        return obj.name

    return obj


def serialize_model_instance(instance):
    """Serialize an instance model as a Python dict.

    :param instance: Instance model.
    :type instance: object
    :return: Instance serialized.
    :rtype: dict
    """
    d = model_to_dict(instance)
    return {k: _adapt(v) for k, v in d.iteritems()}


def extract_process_data():
    """Extract current process name, args, hostname, start time, user and pid.

    :return: Python dict that contains process data.
    :rtype: dict
    """

    p = psutil.Process(os.getpid())

    # Name and args
    if sys.argv[0] == 'manage.py':
        name = sys.argv[1]
        args = ' '.join(sys.argv[2:])
    else:
        name = sys.argv[0]
        args = ' '.join(sys.argv[1:])

    # Machine
    machine = socket.gethostname()

    # Timestamp
    timestamp = datetime.datetime.fromtimestamp(p.create_time()).strftime("%Y-%m-%d %H:%M")

    # User
    user = p.username()

    # PID
    pid = p.pid

    # Interlink ID
    interlink_id = get_process_interlink_id()

    return {
        'interlink_id': interlink_id,
        'name': name,
        'args': args,
        'machine': machine,
        'creation_time': timestamp,
        'user': user,
        'pid': pid,
    }


def i18n_url(url):
    if settings.TRANSLATE_URLS:
        return ugettext_lazy(url)

    return url
