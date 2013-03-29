from django.db import models
import logging

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


logger = logging.getLogger(__file__)


class URLChangeMethod(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.TextField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    method_name = models.TextField()
    current_url = models.TextField(blank=True)
    old_urls = models.ManyToManyField(
        'OldURL',
        related_name='model_method'
    )

    def __unicode__(self):
        return u'{}.{}, with current url {}'.format(
            self.content_object,
            self.method_name,
            self.current_url
        )


class OldURL(models.Model):
    url = models.TextField(unique=True)

    def __unicode__(self):
        return u'{}'.format(self.url)

    def get_new_url(self):
        all_new_urls = set(
            self.model_method
            .exclude(current_url__isnull=True, current_url__exact='')
            .values_list('current_url', flat=True)
        )
        new_url = all_new_urls.pop()
        if len(all_new_urls) > 1:
            logger.warning(
                ('the url {} has multiple new_urls associated with it'
                 '{} was chosen out of {}').format(
                     self,
                     new_url,
                     all_new_urls
                 )
            )
        return new_url
