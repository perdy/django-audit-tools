from __future__ import unicode_literals
"""
Command to prepare Audit in django-application
"""

import logging

from django.core.management.base import BaseCommand

from audit.permissions import register_permissions

logger = logging.getLogger(__name__)


def do_prepare_audit():
    """
    Include steps to prepare audit. Usable from migrations
    """
    register_permissions()


class Command(BaseCommand):
    args = ''
    help = 'Prepare Audit for current django application'

    def handle(self, *args, **options):
        logger.info("Preparing Audit")
        do_prepare_audit()
        logger.info("Audit prepared")
        return True
