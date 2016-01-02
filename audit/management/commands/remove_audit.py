from __future__ import unicode_literals
"""
Command to prepare Audit in django-application
"""

import logging

from django.core.management.base import BaseCommand

from audit.permissions import unregister_permissions

logger = logging.getLogger(__name__)


def do_remove_audit():
    """
    Include steps to remove audit. Usable from migrations.
    """
    unregister_permissions()


class Command(BaseCommand):
    args = ''
    help = 'Remove Audit for current django application'

    def handle(self, *args, **options):
        logger.info("Removing Audit")
        do_remove_audit()
        logger.info("Audit removed")
        return True
