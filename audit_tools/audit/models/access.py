from __future__ import unicode_literals

"""Audit Acess model"""

from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible
from mongoengine import EmbeddedDocument, DateTimeField, StringField, ListField, DictField, IntField, DynamicField, \
    Document, EmbeddedDocumentField, ReferenceField

from audit_tools.audit import settings
from audit_tools.audit.managers import AccessQuerySet
from audit_tools.audit.utils import dynamic_import
from audit_tools.audit.models.process import Process

__all__ = ['Access']


class AccessTime(EmbeddedDocument):
    """Time field for Access document.
    """
    request = DateTimeField(required=True)
    response = DateTimeField()

    def items(self):
        """List items in form (key, value).

        :return: list(tuple())
        """
        return self.to_mongo().items()


class AccessView(EmbeddedDocument):
    """View field for Access document.
    """
    full_name = StringField(required=True)
    app = StringField(required=True)
    name = StringField(required=True)
    args = ListField()
    kwargs = DictField()

    def items(self):
        """List items in form (key, value).

        :return: list(tuple())
        """
        return self.to_mongo().items()


class AccessUser(EmbeddedDocument):
    """User field for Access document.
    """
    id = IntField(required=True)
    username = StringField(required=True)

    def items(self):
        """List items in form (key, value).

        :return: list(tuple())
        """
        return self.to_mongo().items()


class AccessResponse(EmbeddedDocument):
    """Response field for Access document.
    """
    content = DynamicField()
    type = StringField(required=True)
    status_code = IntField(required=True)

    def items(self):
        """List items in form (key, value).

        :return: list(tuple())
        """
        return self.to_mongo().items()


class AccessException(EmbeddedDocument):
    """Exception field for Access document.
    """
    type = StringField(required=True)
    message = StringField(required=True)
    trace = StringField(required=True)

    def items(self):
        """List items in form (key, value).

        :return: list(tuple())
        """
        return self.to_mongo().items()


class AccessRequest(EmbeddedDocument):
    """Request field for Access document.
    """
    path = StringField(required=True)
    GET = DictField()
    POST = DictField()
    COOKIES = DictField()
    METADATA = DictField()
    RAW_METADATA = StringField()

    def items(self):
        """List items in form (key, value).

        :return: list(tuple())
        """
        return self.to_mongo().items()


@python_2_unicode_compatible
class Access(Document):
    """Information gathered from a request and response objects.
    Contains the following structure:

    :cvar interlink_id: Interlink id.
    :cvar request: Request.
    :cvar response: Response content, type and status code.
    :cvar exception: Exception raised.
    :cvar time: Request and response time.
    :cvar view: View full_name, app, name, args and kwargs.
    :cvar user: User id and name.
    :cvar custom: Custom providers field.
    :cvar process: Reference to Process object.
    """
    interlink_id = StringField()
    request = EmbeddedDocumentField(AccessRequest, required=True)
    response = EmbeddedDocumentField(AccessResponse)
    exception = EmbeddedDocumentField(AccessException)
    time = EmbeddedDocumentField(AccessTime, required=True)
    view = EmbeddedDocumentField(AccessView, required=True)
    user = EmbeddedDocumentField(AccessUser)
    custom = DictField()

    # References
    process = ReferenceField(Process)

    # Metadata
    meta = {
        'collection': 'audit_access',
        'indexes': [
            'interlink_id',
            'user.id',
            'request.path',
            'time.request',
            'exception.type',
            ('request.path', 'time.request'),
            ('view.app', 'view.name'),
            ('view.app', 'view.name', 'user.id'),
            ('view.app', 'view.name', 'time.request'),
            ('view.app', 'view.name', 'user.id', 'time.request'),
            ('request.path', 'request.METADATA.REQUEST_METHOD'),
        ],
        'queryset_class': AccessQuerySet,
        'app_label': 'audit',
        'db_alias': settings.DB_ALIAS
    }

    @property
    def url(self):
        """Property that gives access to request__path field.

        :type: str
        """
        return self.request.path

    @url.setter
    def url(self, url):
        self.request.path = url

    @url.deleter
    def url(self):
        del self.request.path

    def get_view(self):
        """Obtains view object that corresponds to this Access instance.

        :return: View.
        :rtype: object
        """
        view = dynamic_import(self.view.full_name)
        return view

    def get_user(self):
        """Obtains User object that corresponds to this Access instance.

        :return: User object.
        :rtype: django.contrib.auth.models.User
        """
        try:
            user = User.objects.get(pk=self.user.id)
        except:
            user = None
        return user

    def is_response(self):
        """Check if this Access contains a response.

        :return: True if contains response.
        :rtype: bool
        """
        return self.response is not None and self.response != {}

    def is_exception(self):
        """Check if this Access contains a exception.

        :return: True if contains exception.
        :rtype: bool
        """
        return self.exception is not None and self.exception != {}

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
        return "Access to view {} from app {} mapped to url {} by user {} ({})".format(
                self.view.name, self.view.app, self.request.path, self.user.username, self.time.request)

    def __str__(self):
        return "Access{{{}, user:{}, url:{}, time:{}}}".format(self.view.full_name, self.user.username,
                                                               self.request.path, self.time.request)
