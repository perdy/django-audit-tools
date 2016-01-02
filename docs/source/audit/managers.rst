========
Managers
========

.. automodule:: audit.managers

Access
======
The following methods are added to the default Access manager:

.. autoclass:: AccessQuerySet
    :members:

Examples::

    # URL /
    Access.objects.filter_by_url(url='/')
    # Filter URLs using regular expression
    Access.objects.filter_by_url(url=r'^/polls/\w*$')
    # Accesses to /polls/ done by user with id 23
    Access.objects.filter_by_url(url='/polls/', user__id=23)

    # Accesses to poll's index
    from polls.views import index
    Access.objects.filter_by_view(fview=index)

    # Accesses that raises an AttributeError exception
    Access.objects.filter_by_exception(exc=AttributeError)

ModelAction
===========
The following methods are added to the default ModelAction manager:

.. autoclass:: ModelActionQuerySet
    :members:

Examples::

    # Actions done over all polls
    from polls.models import Poll
    ModelAction.objects.filter_by_model(klass=Poll)

    # Actions done over a single poll
    poll = Poll.objects.get(id=1)
    ModelAction.objects.filter_by_instance(obj=poll)

    # Actions done over all polls and users
    from django.contrib.auth.models import User
    ModelAction.objects.filter_by_model_list(klass=[Poll, User])

