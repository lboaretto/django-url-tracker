from django.conf import settings, global_settings


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
    ],
    MIDDLEWARE_CLASSES=global_settings.MIDDLEWARE_CLASSES + (
        'url_tracker.middleware.URLChangePermanentRedirectMiddleware',
    ),
    ROOT_URLCONF='tests.urls',
    DEBUG=True,
)
