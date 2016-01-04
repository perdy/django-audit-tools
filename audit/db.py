# -*- encoding: utf-8 -*-
"""
Module to define and create connections with MongoDB.
"""
from __future__ import unicode_literals
import logging

import mongoengine


logger = logging.getLogger(__name__)


def mongodb_connect(connection, alias):
    user = connection.get('USER', None)
    password = connection.get('PASSWORD', None)
    host = connection.get('HOST', 'localhost')
    port = connection.get('PORT', 27017)
    name = connection.get('NAME', 'audit')
    replica_set = connection.get('REPLICA_SET', '')

    if isinstance(host, (list, tuple)) and isinstance(port, (list, tuple)) and len(host) == len(port):
        hosts_list = ["{}:{}".format(h, p) for h, p in zip(host, port)]
        hosts_str = ",".join(hosts_list)
        options = "?replicaSet={}".format(replica_set)
    else:
        hosts_str = "{}:{}".format(host, port)
        options = ""

    if user and password:
        uri = 'mongodb://{}:{}@{}/{}{}'.format(user, password, hosts_str, name, options)
    else:
        uri = 'mongodb://{}/{}{}'.format(hosts_str, name, options)

    try:
        mongoengine.connect(name, host=uri, alias=alias)
    except mongoengine.ConnectionError as e:
        logger.error('Database connection error: %s', e.message, exc_info=e)
        raise e
