from django.conf.urls.defaults import patterns, url
from django.views.generic import TemplateView


urlpatterns = patterns(
    '',
    url(
        r'^testmodel/(\w+)/$',
        TemplateView.as_view(template_name="_.html"),
        name="test-url"
    ),
)
