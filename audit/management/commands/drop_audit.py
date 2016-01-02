from __future__ import unicode_literals

"""Command to delete Audit database.
"""
import datetime
import logging

from django.core.management.base import BaseCommand

from audit.models import Access, Process, ModelAction

LOG = logging.getLogger(__name__)


def drop_audit(init_date=None, end_date=None):
    """Delete all Documents in Audit database.
    """
    if not init_date and not end_date:
        ModelAction.drop_collection()
        Access.drop_collection()
        Process.drop_collection()
    else:
        ModelAction.objects.filter(timestamp__gte=init_date, timestamp__lte=end_date).delete()
        Access.objects.filter(time__request__gte=init_date, time__request__lte=end_date).delete()
        Process.objects.filter(creation_time__gte=init_date, creation_time__lte=end_date).delete()


class Command(BaseCommand):
    args = 'init_date end_date'
    date_format = '%d/%m/%Y'
    time_format = '%H:%M:%S'
    datetime_format = date_format + '-' + time_format
    help = 'Drop Audit database, deleting all data.'

    option_list = BaseCommand.option_list

    def handle(self, *args, **options):
        init_date = None
        end_date = None

        if len(args) == 1:
            init_date = datetime.datetime.strptime(args[0], self.date_format)
            end_date = datetime.datetime.now()
        elif len(args) == 2:
            init_date = datetime.datetime.strptime(args[0], self.date_format)
            end_date = datetime.datetime.strptime(args[1], self.date_format)

        resp = ''
        while not resp or resp.lower() not in ('y', 'n'):
            resp = raw_input('Delete Audit database? [Y|n] ')
            if resp == '':
                resp = 'y'
        delete = resp.lower() == 'y'

        if delete:
            drop_audit(init_date=init_date, end_date=end_date)
        else:
            print("Process aborted")

        return 0
