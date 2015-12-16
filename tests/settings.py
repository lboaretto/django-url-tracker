import django

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
    'django.contrib.auth',
    'django.contrib.contenttypes',
)

if django.VERSION[:2] < (1, 6):
    TEST_RUNNER = 'discover_runner.DiscoverRunner'

MIDDLEWARE_CLASSES = (
    'url_tracker.middleware.URLChangePermanentRedirectMiddleware',
)
ROOT_URLCONF = 'tests.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
    },
]
