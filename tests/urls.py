from django.conf.urls.defaults import patterns, url
from django.views.generic import TemplateView


urlpatterns = patterns(
    '',
    url(
        r'^(?P<slug>\w+)/$',
        TemplateView.as_view(template_name="_.html"),
        name="project"
    ),
)
