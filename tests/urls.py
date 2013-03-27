from django.conf.urls.defaults import patterns, url
from django.views.generic import TemplateView


def dummy_404_view(*args, **kwargs):
    return

urlpatterns = patterns(
    '',
    url(
        r'^(?P<slug>\w+)/$',
        TemplateView.as_view(template_name="_.html"),
        name="project"
    ),
    handler404 = 'test.urls.dummy_404_view'

)
