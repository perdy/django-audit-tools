from __future__ import unicode_literals
"""Audit Process model"""

from django.utils.encoding import python_2_unicode_compatible
from mongoengine import Document, StringField, IntField, DateTimeField

from audit import settings


@python_2_unicode_compatible
class Process(Document):
    """Represents a process that launch a django management command.

    :cvar name: Process name.
    :cvar args: Process args.
    :cvar machine: Machine that launched this process.
    :cvar user: User that launched this process.
    :cvar pid: Process pid.
    :cvar creation_time: Time when process was launched.
    """
    interlink_id = StringField()
    name = StringField(required=True)
    args = StringField()
    machine = StringField(required=True)
    user = StringField(required=True)
    pid = IntField(required=True, unique_with=('machine', 'creation_time'))
    creation_time = DateTimeField(required=True)

    # Metadata
    meta = {
        'collection': 'audit_process',
        'indexes': [
            'interlink_id',
            ('pid', 'machine', '-creation_time')
        ],
        'app_label': 'audit',
        'db_alias': settings.DB_ALIAS,
    }
    meta['indexes'].extend(settings.PROCESS_INDEXES)

    def items(self):
        """List items in form (key, value).

        :return: list(tuple())
        """
        return self.to_mongo().items()

    def __str__(self):
        return "{} user:{} machine:{} creation_time:{}".format(self.name, self.user, self.machine, self.creation_time)


