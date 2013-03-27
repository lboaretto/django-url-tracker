from django.conf.urls.defaults import patterns, url


urlpatterns = patterns(
    '',
    url(
        r'^(?P<slug>\w+)/$',
        TemplateView.as_view(template_name="_.html"),
        name="project"
    ),
)
