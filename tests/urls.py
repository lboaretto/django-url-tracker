from django.conf.urls.defaults import patterns, url
from django.views.generic import DetailView

from .models import TestModel

urlpatterns = patterns(
    '',
    url(
        r'^testmodel/(?P<slug>\w+)/$',
        DetailView.as_view(
            model=TestModel,
            template_name='_.html'
        ),
        name="model-detail"
    ),
)
