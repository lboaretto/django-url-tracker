import url_tracker

from django.core.urlresolvers import reverse
from django.db import models


class TestModel(url_tracker.URLTrackingMixin, models.Model):
    slug = models.SlugField(max_length=20, null=True, blank=True)

    def get_absolute_url_using_reverse(self):
        return reverse('project', kwargs={'slug': self.slug})

    @models.permalink
    def get_absolute_url_using_permalink(self):
        return ('project', (), {'slug': self.slug})

    def slug_or_none(self):
        return self.slug or None

    url_tracking_methods = [
        'get_absolute_url_using_reverse',
        'get_absolute_url_using_permalink',
        'slug_or_none'
    ]

url_tracker.track_url_changes_for_model(TestModel)
