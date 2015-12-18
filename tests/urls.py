import django
from django.views.generic import DetailView

try:
    from django.conf.urls import url
except ImportError:
    from django.conf.urls.defaults import url

from .models import TestModel

urlpatterns = [
    url(
        r'^testmodel/(?P<slug>\w+)/$',
        DetailView.as_view(
            model=TestModel,
            template_name='_.html'
        ),
        name="model-detail"
    ),
]

if django.VERSION < (1, 8, 0):
    try:
        from django.conf.urls import patterns
    except ImportError:
        from django.conf.urls.defaults import patterns
    urlpatterns = patterns('', *urlpatterns)
