import url_tracker

from django.core.urlresolvers import reverse
from django.db import models


class TestModel(url_tracker.URLTrackingMixin, models.Model):
    slug = models.SlugField(max_length=20, null=True, blank=True)
    text = models.TextField(max_length=20, null=True, blank=True)

    def get_absolute_url(self):
        return reverse('test-url', args=(self.slug,))

    def get_text(self):
        return self.text

    url_tracking_methods = [
        'get_absolute_url',
        'get_text'
    ]
