from django.conf import global_settings

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
SECRET_KEY = "_"
INSTALLED_APPS = (
    'url_tracker',
    'tests',
    'django.contrib.contenttypes',
)

MIDDLEWARE_CLASSES = global_settings.MIDDLEWARE_CLASSES + (
    'url_tracker.middleware.URLChangePermanentRedirectMiddleware',
)
ROOT_URLCONF = 'tests.urls'
DEBUG = True
