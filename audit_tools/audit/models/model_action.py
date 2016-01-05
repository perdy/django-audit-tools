from __future__ import unicode_literals

"""Audit ModelAction model"""

import datetime

from django.utils.encoding import python_2_unicode_compatible
from mongoengine import EmbeddedDocument, StringField, DictField, Document, EmbeddedDocumentField, DateTimeField, \
    ReferenceField

from audit_tools.audit import settings
from audit_tools.audit.managers import ModelActionQuerySet
from audit_tools.audit.models import Access, Process
from audit_tools.audit.utils import dynamic_import

__all__ = ['ACTIONS', 'ModelAction']


class ACTIONS(object):
    """Enumerate class for actions over models.
    """
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'


ACTION_CHOICES = (
    (ACTIONS.CREATE, ACTIONS.CREATE),
    (ACTIONS.UPDATE, ACTIONS.UPDATE),
    (ACTIONS.DELETE, ACTIONS.DELETE),
)


class ModelActionModel(EmbeddedDocument):
    """Model field for ModelAction document.
    """
    full_name = StringField(required=True)
    app = StringField(required=True)
    name = StringField(required=True)

    def items(self):
        """List items in form (key, value).

        :return: list(tuple())
        """
        return self.to_mongo().items()


class ModelActionContent(EmbeddedDocument):
    """Content field for ModelAction document.
    """
    old = DictField()
    new = DictField()
    changes = DictField()

    def items(self):
        """List items in form (key, value).

        :return: list(tuple())
        """
        return self.to_mongo().items()


class ModelActionInstance(EmbeddedDocument):
    """Instance field for ModelAction document.
    """
    id = StringField(required=True)
    description = StringField(required=True)

    def items(self):
        """List items in form (key, value).

        :return: list(tuple())
        """
        return self.to_mongo().items()


@python_2_unicode_compatible
class ModelAction(Document):
    """Information from create, update or delete operations over a model.
    Contains the following structure:

    :cvar model: Model full_name, app and name.
    :cvar action: Create, update or delete action.
    :cvar content: Old and new values and changes.
    :cvar instance: Instance object id and description.
    :cvar timestamp: Time when action occurs.
    :cvar access: Reference to Access object.
    :cvar process: Reference to Process object.
    """
    model = EmbeddedDocumentField(ModelActionModel)
    action = StringField(required=True, choices=ACTION_CHOICES)
    content = EmbeddedDocumentField(ModelActionContent)
    instance = EmbeddedDocumentField(ModelActionInstance)
    timestamp = DateTimeField(default=datetime.datetime.now())

    # References
    access = ReferenceField(Access)
    process = ReferenceField(Process)

    # Metadata
    meta = {
        'collection': 'audit_model_action',
        'indexes': [
            'timestamp',
            ('action', 'timestamp'),
            ('model.app', 'model.name'),
            ('model.app', 'model.name', 'action'),
            ('model.app', 'model.name', 'instance.id'),
            ('model.app', 'model.name', 'timestamp'),
            ('model.app', 'model.name', 'action', 'timestamp'),
            ('model.app', 'model.name', 'instance.id', 'timestamp'),
        ],
        'queryset_class': ModelActionQuerySet,
        'app_label': 'audit',
        'db_alias': settings.DB_ALIAS,
    }

    @property
    def changes(self):
        """Property that gives access to content__changes field.

        :type: dict
        """
        return self.content.changes

    @changes.setter
    def changes(self, changes):
        self.content.changes = changes

    @changes.deleter
    def changes(self):
        del self.content.changes

    def get_model(self):
        """Obtains Model class that corresponds to this ModelAction instance.

        :return: Model class.
        :rtype: object
        """
        try:
            model = dynamic_import(self.model.full_name)
        except:
            raise TypeError('Model {} does not exist.'.format(self.model.full_name))
        return model

    def get_instance(self):
        """Obtains instance object that corresponds to this ModelAction instance.

        :return: Instance object.
        :rtype: object
        """
        model = dynamic_import(self.model.full_name)
        try:
            instance = model.objects.get(pk=self.instance.id)
        except:
            instance = None

        return instance

    def items(self):
        """List items in form (key, value).

        :return: list(tuple())
        """
        return self.to_mongo().items()

    def verbose_str(self):
        """Verbose string representation.

        :return: Verbose string representation.
        :rtype: str
        """
        return "{} instance {} of model {} from app {} ({})".format(
            self.action, self.instance.id, self.model.name, self.model.app, self.timestamp)

    def __str__(self):
        return "ModelAction{{{}({}), action:{}, time:{}}}".format(
            self.model.full_name, self.instance.id, self.action, self.timestamp)
