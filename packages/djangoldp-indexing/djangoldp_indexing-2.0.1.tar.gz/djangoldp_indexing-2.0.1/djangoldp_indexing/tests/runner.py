#!/usr/bin/env python
import sys
import yaml

import django
from django.conf import settings as django_settings
from djangoldp.conf.ldpsettings import LDPSettings

# create a test configuration
config = {
    # add the packages to the reference list
    'ldppackages': ['djangoldp_indexing', 'djangoldp_indexing.tests'],

    # required values for server
    'server': {
        'SECRET_KEY': 'test-key-not-for-production',
        'DATABASES': {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:'
            }
        },
        'INSTALLED_APPS': [
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'rest_framework',
            'guardian',
            'djangoldp',
            'djangoldp_indexing',
            'djangoldp_indexing.tests'
        ]
    }
}

ldpsettings = LDPSettings(config)
django_settings.configure(ldpsettings)
django.setup()

from django.test.runner import DiscoverRunner
test_runner = DiscoverRunner(verbosity=1)
failures = test_runner.run_tests(['djangoldp_indexing.tests'])
if failures:
    sys.exit(failures) 