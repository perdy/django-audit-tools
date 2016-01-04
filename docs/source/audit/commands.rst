========
Commands
========

Django commands for ebury-audit application.

drop_audit
----------

Drop audit database. If only initial date is given, data from that day to now. If the two dates are provided, data will be deleted in that range. Delete all data otherwise.

Syntax::

    python manage.py drop_audit [init_date] [end_date]

Example::

    python manage.py drop_audit
    python manage.py drop_audit 01/01/2000
    python manage.py drop_audit 01/01/2000 01/02/2000

prepare_ebury_audit
-------------------
Prepare system for ebury-audit application adding needed permissions, tables...

Syntax::

    python manage.py prepare_ebury_audit

prepare_ebury_audit
-------------------
Remove ebury-audit application from system.

Syntax::

    python manage.py remove_ebury_audit

