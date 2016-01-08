# -*- coding: utf-8 -*-
import os
import sys

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'audit_tools.tests.settings')

if hasattr(django, "setup"):
    django.setup()

from django_nose import NoseTestSuiteRunner

test_runner = NoseTestSuiteRunner(verbosity=1)
failures = test_runner.run_tests(["audit_tools"])

if failures:
    sys.exit(failures)
