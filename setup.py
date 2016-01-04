#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

import audit

with open(os.path.join(os.path.dirname(__file__), 'requirements.txt'), 'r') as f:
    requires = f.read().splitlines()


class Tox(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = ''

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox
        import shlex
        errno = tox.cmdline(args=shlex.split(self.tox_args))
        sys.exit(errno)


setup(
    name='django-audit-tools',
    version=audit.__version__,
    description=audit.__description__,
    long_description='\n'.join([open('README.rst').read(), open('CHANGELOG').read()]),
    author=audit.__author__,
    author_email=audit.__email__,
    maintainer=audit.__author__,
    maintainer_email=audit.__email__,
    url=audit.__url__,
    download_url=audit.__url__,
    packages=[
        'audit',
    ],
    include_package_data=True,
    install_requires=requires,
    license=open('LICENSE').read(),
    zip_safe=False,
    keywords='python, django, database, requests, audit, logging',
    classifiers=[
        # Framework
        'Framework :: Django',
        # Environment
        'Environment :: Web Environment',
        # Intended Audience:
        'Intended Audience :: Support',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        # License
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        # Natural Language
        'Natural Language :: English',
        # Operating System
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        # Programming Language
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        # Topic
        'Topic :: Software Development',
        'Topic :: Software Development :: Bug Tracking',
        'Topic :: System :: Logging',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    test_suite='tests',
    tests_require=['tox'],
    cmdclass={'test': Tox},
)
