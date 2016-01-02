================
Custom providers
================

Custom provider is a mechanism that permits an application to add custom data to *Access* logs. A single provider can be specified for each app.

The next example define a provider that returns polls associated to current user::

    def poll_provider(request):
        user = User.objects.get(pk=request.user.id)
        polls = Poll.objects.filter(user=user)
        polls_names = [p.name for p in polls]

        res = {
            'names': poll_names,
            'num_polls': len(poll_names),
        }

        return res

If this provider is defined inside :py:mod:`polls.utils` then must be set in :py:const:`.settings.AUDIT_CUSTOM_PROVIDER`::

    AUDIT_CUSTOM_PROVIDER = {
        'polls': 'polls.utils.poll_provider',
    }


This provider will result in an additional field inside :py:class:`~.models.Access` named 'polls'::

    {
        ...
        custom = {
            polls = {
                names = [ "poll_1", "poll_2" ],
                num_polls = 2
            }
        }
    }

