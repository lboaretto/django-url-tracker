from django.db import models
import logging

from django.contrib.contenttypes.models import ContentType
try:  # new import added in Django 1.7
    from django.contrib.contenttypes.fields import GenericForeignKey
except ImportError:
    from django.contrib.contenttypes import generic
    GenericForeignKey = generic.GenericForeignKey


logger = logging.getLogger(__file__)


class URLChangeMethod(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.TextField()
    content_object = GenericForeignKey('content_type', 'object_id')

    method_name = models.TextField()
    current_url = models.TextField(blank=True)
    old_urls = models.ManyToManyField(
        'OldURL',
        related_name='model_method'
    )

    class Meta:
        app_label = 'url_tracker'

    def __unicode__(self):
        return '{0}.{1}, with current url {2}'.format(
            self.content_object,
            self.method_name,
            self.current_url
        )


class OldURL(models.Model):
    url = models.TextField(unique=True)

    class Meta:
        app_label = 'url_tracker'

    def __unicode__(self):
        return '{0}'.format(self.url)

    def get_new_url(self):
        all_new_urls = self.model_method.order_by('-current_url').values_list('current_url', flat=True)
        new_url = all_new_urls[0]
        if len(all_new_urls) > 1:
            logger.warning(
                ('the url {0} has multiple new_urls associated with it'
                 '{1} was chosen out of {2}').format(
                     self,
                     new_url,
                     all_new_urls
                 )
            )
        return new_url
