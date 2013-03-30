import url_tracker

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import signals


def reverse_model(slug):
        return reverse('model-detail', kwargs={'slug': slug})


class TestModel(url_tracker.URLTrackingMixin, models.Model):
    slug = models.SlugField(max_length=20, null=True, blank=True)
    text = models.TextField(max_length=20, null=True, blank=True)

    def get_absolute_url(self):
        return reverse_model(self.slug)

    def get_text(self):
        return self.text

    url_tracking_methods = [
        'get_absolute_url',
        'get_text'
    ]


class RemoveSignals(object):
    def tearDown(self):
        def remove_reciever_from_signal(signal):
            signal.receivers = []
        remove_reciever_from_signal(signals.post_save)
        remove_reciever_from_signal(signals.pre_save)
