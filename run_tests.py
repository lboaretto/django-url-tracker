#!/usr/bin/env python
from django.conf import settings, global_settings
from django.core import management


if __name__ == '__main__':
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'url_tracker',
            'tests',
            'django.contrib.contenttypes',
            'django_nose',
        ],
        MIDDLEWARE_CLASSES=global_settings.MIDDLEWARE_CLASSES + (
            'url_tracker.middleware.URLChangePermanentRedirectMiddleware',
        ),
        ROOT_URLCONF='tests.urls',
        DEBUG=True,
        TEST_RUNNER='django_nose.NoseTestSuiteRunner',
        NOSE_ARGS=[
            '--with-coverage',
            '--cover-package=url_tracker',
            '--cover-branches',
            '--with-specplugin'
        ]
    )
    management.call_command('test')
